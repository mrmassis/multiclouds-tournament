#!/usr/bin/env python


import pika;
import time;
import sys;
import os;
import datetime;
import ConfigParser;
import json;
import logging;
import logging.handlers;

from lib.database     import Database;
from multiprocessing  import Process, Queue, Lock;
from lib.scheduller   import Roundrobin;
from lib.amqp         import RabbitMQ_Publish, RabbitMQ_Consume;





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
class Division(Process):

    """
    Class Division:
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    * run == division main loop.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __dNumb;
    __dName;
    __dConf;
    __dBase;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, dNumb, dName, dConf, dbase):
        super(Division, self).__init__(name=dName);

        self.__dNumb = dNumb;
        self.__dName = dName;
        self.__dConf = dConf;
        self.__dBase = dBase;

        ## LOG:
        logger.info('STARTED DIVISION %s', dName);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## Brief: division main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        ## Obtain the initial base used to check when will be held the round 1.
        timeOld = datetime.datetime.now();

        while True:

            ## Obtain the current time. The value is used to calculate the time
            ## difference.
            timeNow = datetime.datetime.now();

            ## Elapsed time of the last round until now. Used to check the next
            ## round.
            elapsedT = timeNow - timeOld;

            if divmod(elapsedT.total_seconds(),60)[0] >= self.__dConf['round']:
                 ## LOG:
                 logger.info('ROUND FINISHED!');

                 ## Calculates attributes (score and history) of each player in
                 ## the division.
                 self.__calculate_attributes();

                 timeOld = datetime.datetime.now();

            time.sleep(self.__dConf['time_step']);

        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: Calculate attributes of each player in the  division.
    ## ------------------------------------------------------------------------
    ## 
    def __calculate_attributes(self):

        query = 'SELECT';

        #valRet = [];

        #attributesPlayers = [];
        #for player in valRet:

        #     attributesPlayers = {
        #         'name'     : player[0], 
        #         'score'    : player[1],
        #         'historic' : player[2]
        #     }


        ## Cria uma lista com os players presentes e os scores atuais deles.
        ## Obtain o historico de acao desde o ultimo round (Tabela de requests).
        ## Atualiza os scores e os historicos.
        ## grava novamente na base.

        query = 'UPDATE';
        return 0;
## END.






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
        configs = self.__get_configs(CONFIG_FILE);

        ## Get which route is used to deliver the message to the MCT_Dispatch.
        self.__routeDispatch = configs['amqp_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, configs['amqp_consume']);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish=RabbitMQ_Publish(configs['amqp_publish']);

        ## Intance a new object to handler all operation in the local database
        self.__dbConnection = Database(configs['database']);

        ## Select the scheduller algorithm responsible for selection of the be-
        ## st player in a division.
        if configs['scheduller']['approach'] == 'roundrobin':
            self.__scheduller = Roundrobin(configs['scheduller']['restrict']);

        ## This list store the thread IDs that represet each division started.
        self.__threadsId = [];

        ## Instance the divisions that will be used in MCT:
        for divNumb in range(1, int(configs['main']['num_divisions']) + 1):
             divName = 'division' + str(divNumb);
             divConf = configs[divName];

             division=Division(divNumb, divName, divConf, self.__dbConnection);
             division.daemon = True;
             division.start();

             self.__threadsId.append(division);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: grecefull finish the divisions.
    ## ------------------------------------------------------------------------
    ##
    def gracefull_stop(self):
        for thread in self.__threadsId:
            thread.terminate();
            thread.join();

        ## LOG:
        logger.info('GRACEFULL STOP ...');
        return 0;


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
                ## [0] == GET RESOUCES INF.                                  ##
                ## --------------------------------------------------------- ##
                if   int(message['code']) == 0:

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

        #valRet = [] or self.__dbConnection.select_query(query);

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
    ## TODO: testar.
    ##
    def __get_division(self, playerId):
        ## LOG:
        logger.info('INSPECT REQUEST!');

        ## Setting 
        division = -1;

        query = "SELECT division FROM PLAYER WHERE name='" + playerId + "'";

        valRet = [] or self.__dbConnection.select_query(query);

        if valRet != []:
            division = valRet[0][0];

        return division;


    ##
    ## BRIEF: create a new instance.
    ## ------------------------------------------------------------------------
    ## @PARAM int division ==.
    ## @PARAM dict message ==.
    ##
    def __add_instance_inf(self, division, message):
        ##.
        message['retId'] = message['reqId'];

        ## Select one player able to comply a request to create VM.
        message['destAdd'] = self.__get_player(division, message['playerId']);

        ## TODO: se for vazio o message entao retorna erro e retorna para o re-
        ##       quisitante.

        return message;
 

    ##
    ## BRIEF: delete an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM int division ==.
    ## @PARAM dict message ==.
    ##
    def __del_instance_inf(self, division, message):
        return {};


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

        valRet = [] or self.__dbConnection.select_query(query);

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
    ## @PARAM int division.
    ## TODO: implementar o scheduler, entrada uma lista de players.
    ##
    ##
    def __get_choice_player(self, division, playerIdRequest):

       ##
       query = "SELECT * FROM PLAYER WHERE division='" + division + "'";
       
       ## Choice player address:
       playerAddress = '20.0.0.30';

       valRet = [] or self.__dbConnection.select_query(query);

       if valRet != []:
           ## Perform the player selection.
           playerAddress = self.__scheduller.run(valRet[0], playerIdRequest);

       ## 
       return playerAddress;


    ##
    ## BRIEF: get config options.
    ## ------------------------------------------------------------------------
    ## @PARAM str configName == file with configuration.
    ##
    def __get_configs(self, configName):
        cfg = {};

        config = ConfigParser.ConfigParser();
        config.readfp(open(configName));

        ## Scan the configuration file and get the relevant informations and sa
        ## ve then in cfg dictionary.
        for section in config.sections():
            cfg[section] = {};

            for option in config.options(section):
                cfg[section][option] = config.get(section,option);

        return cfg;
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
        mctReferee.gracefull_stop();

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF.

