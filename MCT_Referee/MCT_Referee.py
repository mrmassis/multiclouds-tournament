#!/usr/bin/env python


import pika;
import time;
import sys;
import os;
import datetime;
import json;
import logging;
import logging.handlers;

from lib.database     import Database;
from multiprocessing  import Process, Queue, Lock;
from lib.scheduller   import *;
from lib.amqp         import RabbitMQ_Publish, RabbitMQ_Consume;
from lib.utils        import *;





###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE   = '/etc/mct/mct_referee.ini';
LOG_NAME      = 'MCT_Referee';
LOG_FORMAT    = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME  = '/var/log/mct/mct_referee.log';








###############################################################################
## LOG                                                                       ##
###############################################################################
## Create a handler and define the output filename and the max size and max nun
## ber of the files (1 mega = 1048576 bytes).
handler= logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                              maxBytes=1048576,
                                              backupCount=10);

## Create a foramatter that specific the format of log and insert it in the log
## handler. 
formatter = logging.Formatter(LOG_FORMAT);
handler.setFormatter(formatter);

## Set up a specific logger with our desired output level (in this case DEBUG).
## Before, insert the handler in the logger object.
logger = logging.getLogger(LOG_NAME);
logger.setLevel(logging.DEBUG);
logger.addHandler(handler);








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Referee(RabbitMQ_Consume):

    """
    Class MCT_Referee: start and mantain the MCT referee.
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    ** run            == create the divisions and wait in loop.
    ** gracefull_stop == grecefull finish the divisions.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __threadsId     = None;
    __allQueues     = None;
    __routeDispatch = None;
    __dbConnection  = None;
    __scheduller    = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        ## Get the configurations related to the execution of the divisions de
        ## fined by the User.
        configs = get_configs(CONFIG_FILE);

        ## Get which route is used to deliver the message to the MCT_Dispatch.
        self.__routeDispatch = configs['amqp_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, configs['amqp_consume']);

        ## Credentials:
        configs['amqp_publish']['user'] = configs['rabbitmq']['user'];
        configs['amqp_publish']['pass'] = configs['rabbitmq']['pass'];

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish=RabbitMQ_Publish(configs['amqp_publish']);

        ## Intance a new object to handler all operation in the local database
        self.__db = Database(configs['database']);

        ## Select the scheduller algorithm responsible for selection of the be-
        ## st player in a division.
        if   configs['scheduller']['approach'] == 'roundrobin':
            self.__scheduller = Roundrobin(configs['scheduller']['restrict']);

        elif configs['scheduller']['approach'] == 'bestscores':
            self.__scheduller = Bestscores(configs['scheduller']['restrict']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: method invoked when the pika receive a message.
    ## ------------------------------------------------------------------------
    ## @PARAM pika.Channel              channel    = the communication channel.
    ## @PARAM pika.spec.Basic.Deliver   method     = 
    ## @PARAM pika.spec.BasicProperties properties = 
    ## @PARAM str                       message    = message received.
    ##
    def callback(self, channel, method, properties, message):

        ## LOG:
        logger.info('MESSAGE %s RECEIVED FROM: %s.',message,properties.app_id);

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        ## The json.loads translate a string containing JSON data into a Python
        ## dictionary format.
        message = json.loads(message);
 
        ## Check the messsge received.Verify if all fields are presents and are
        ## in correct form.
        valRet = self.__inspect_request(message);

        if valRet == 0:

            ## Check if is a request or a response received from the apropriate
            ## player. When message['retId'] equal a '' the msg is a request.
            if message['retId'] == '':

                ## Get which division than player belong.It is necessary to get
                ## the player list able to meet the request.
                division = self.__get_division(message['playerId']);

                ## --------------------------------------------------------- ##
                ## DIVISION INVALID (-1).                                    ##
                ## --------------------------------------------------------- ##
                if division == -1:
                    message['retId' ] = '';
                    message['status'] = 0 ;

                ## --------------------------------------------------------- ##
                ## [0] == GET RESOUCES INF.                                  ##
                ## --------------------------------------------------------- ##
                elif int(message['code']) == 0:

                    ## Get all resources available to a division. Check in db.
                    message['data'] = self.__get_resources_inf(division);

                ## --------------------------------------------------------- ##
                ## [1] CREATE A NEW INSTANCE.                                ##
                ## --------------------------------------------------------- ##
                elif int(message['code']) == 1:
                    message = self.__add_instance(division, message);

                ## --------------------------------------------------------- ##
                ## [2] DELETE AN INSTANCE.                                   ##
                ## --------------------------------------------------------- ##
                elif int(message['code']) == 2:
                    message = self.__del_instance(division, message);
    
            else:
                ## Set the field to forward value:
                message['retId'] = '';

            self.__publish.publish(message, self.__routeDispatch);

        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: check if reques is valid.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __inspect_request(self, request):
        ## LOG:
        logger.info('INSPECT REQUEST!');

        key = request['code'];

        query = "SELECT fields FROM FIELDS WHERE operation='" + str(key) + "'";

        #valRet = [] or self.__db.select_query(query);

        #if valRet != []:
        #    fields = valRet[0][0];

        #     for field in fields:
        #         if not request.has_key(field):
        #             print "LOG: missed field " + key;
        #             return 1;

        #    return 0;

        return 0;


    ##
    ## BRIEF: get the player's division.
    ## ------------------------------------------------------------------------
    ## @PARAM str playerId == player identifier.
    ##
    def __get_division(self, playerId):
        ## LOG:
        logger.info('INSPECT REQUEST!');

        ## Setting 
        division = -1;

        query = "SELECT division FROM PLAYER WHERE name='" + playerId + "'";

        valRet = [] or self.__db.select_query(query);

        if valRet != []:
            division = valRet[0][0];

        return division;


    ##
    ## BRIEF: create a new instance.
    ## ------------------------------------------------------------------------
    ## @PARAM int division ==.
    ## @PARAM dict message ==.
    ##
    def __add_instance(self, division, message):
        ## 
        timeStamp = str(datetime.datetime.now());

        ## RETURN: If retId !='' the request is return from the player destiny. 
        if message['retId'] != '':

            message['destAdd'] = '';
            message['retId'  ] = '';

            ## LOG:
            logger.info('RETURN FROM REQUEST ADD_INSTNACE IS: ' + str(status));

            ## Here is check the status, and setting the database to record the
            ## result of action.
            query  = "INSERT INTO INSTANCE (";
            query += "player_id, ";
            query += "request_id, ";
            query += "status, ";
            query += "timestamp_received";
            query += ") VALUES (%s, %s, %s, %s, %s)";
            value  = (playerId, requestId, actionId, status, timeStamp);

            valRet = self.__db.insert_query(query, value);

        ## SENDTO: If 'retId == empty' the request is go to the player destiny.
        else:

            ## Select one player able to comply a request to create VM. Inside
            ## these method is selected the scheduller approach.
            selectedPlayer = self.__get_player(division, message['playerId']);

            if selectedPlayer != {}:
                name = selectedPlayer['name'];
                addr = selectedPlayer['addr'];

                ## LOG:
                logger.info('SELECTED THE PLAYER '+name+'address '+str(addr));

                ## Set the message to be a forward message (perform a map). Send
                ## it to the destine and waiting the return.
                message['retId'] = message['reqId'];

                ## Set the target address. The target addr is the player's addrs
                ## tha will accept the request.
                message['destAdd'] = addr;

                ## LOG:
                logger.info('MESSAGE ' + str(message));

            else:
                ## LOG:
                logger.info('THERE IS NOT PLAYER ABLE TO EXEC THE REQUEST!');

                ## Case not found a player to exec the request setting status
                ## to error and return the message to origin.
                message['status'] = 0; 

        return message;
 

    ##
    ## BRIEF: delete an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM int division == the player division .
    ## @PARAM dict message == message with some datas to delete an instance.
    ##
    def __del_instance(self, division, message):
        ## LOG:
        logger.info('DELETE MESSAGE: %s', str(message));

        ## tem que olhar na base para saber quem atendeu!
        ## pegar o address
        ## mandar um request de apagar
        ## aguardar.
        ## retornar para a origin o status;

        ## TODO: melhorar, da para saber quem eh olhando a base das intancias. Dai recupra o address!!!!
        print message;

        ## Tem que recuperar quem esta executando a instancia.
        ## Mandar um destroi.
        ## E retornar. 
        message['status'] = 1;

        return message;


    ##
    ## BRIEF: get the resources info to specfic division.
    ## ------------------------------------------------------------------------
    ## @PARAM int division.
    ##
    def __get_resources_inf(self, division):
        resouces = {};

        ## Mount the database query: 
        query  = "SELECT ";
        query += "vcpu, memory, disk, vcpu_used, memory_used, disk_used ";
        query += "FROM RESOURCE WHERE ";
        query += "division='" + str(division) + "'";

        valRet = [] or self.__db.select_query(query);

        if valRet != []:

            resources = {
                'vcpu'          : valRet[0][0],
                'memory_mb'     : valRet[0][1],
                'disk_mb'       : valRet[0][2],
                'vcpu_used'     : valRet[0][3],
                'memory_mb_used': valRet[0][4],
                'disk_mb_used'  : valRet[0][5]
            }

        return resources;


    ##
    ## BRIEF: choice the best player to perform the request.
    ## ------------------------------------------------------------------------
    ## @PARAM int division == division to considerated.
    ## @PARAM str playerId == player's id who made the request.
    ##
    def __get_player(self, division, playerId):

       selectedPlayer = {};

       ## Genereate the query to select the players belong to specific division.
       query  = "SELECT * FROM PLAYER WHERE ";
       query += "division='" + str(division) + "' and ";
       query += "name!='"    + str(playerId) + "'";
       
       valRet = [] or self.__db.select_query(query);

       if valRet != []:
           ## Perform the player selection. Utilize the scheduller algorithm se
           ## lected before.
           playerOrdenedList = self.__scheduller.run(valRet);

           if playerOrdenedList != []: 
               selectedPlayer = playerOrdenedList[0];
           else:
               selectedPlayer = {};

       return selectedPlayer;
## END.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    ## LOG:
    logger.info('EXECUTION STARTED...');

    try:
        mctReferee = MCT_Referee();
        mctReferee.consume();

    except KeyboardInterrupt, error:
        pass;

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF.

