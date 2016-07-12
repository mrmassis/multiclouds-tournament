#!/usr/bin/env python


import sys;
import json;
import datetime;
import logging;
import logging.handlers;

from lib.utils    import *;
from lib.database import Database;
from lib.amqp     import RabbitMQ_Publish, RabbitMQ_Consume;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE      = '/etc/mct/mct_dispatch.ini';
AGENT_ROUTE      = 'mct_agent';
AGENT_IDENTIFIER = 'MCT_Dispatch';
AGENT_EXCHANGE   = 'mct_exchange';
AGENT_QUEUE      = 'agent';
LOG_NAME         = 'MCT_Dispatch';
LOG_FORMAT       = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME     = '/var/log/mct/mct_dispatch.log';






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
class MCT_Dispatch(RabbitMQ_Consume):

    """
    Dispatch to appropriate destinations requires received from players or divi
    sions.
    ---------------------------------------------------------------------------
    callback == method invoked when the pika receive a message.
    
    __recv_message_referee == receive message from referee.
    __send_message_referee == send message to referee.
    __append_query         == store the request identifier.
    __remove_query         == store the request identifier.
    __inspect_request      == check if all necessary fields are in request.
    __get_configs          == obtain all configuration from conffiles.

    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __publish       = None;
    __divisions    = [];
    __configs      = None;
    __dbConnection = None;
    __rabbitUser   = None;
    __rabbitPass   = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        configs = get_configs(CONFIG_FILE);

        ## Get which 'route' is used to deliver the message to the MCT_Referee.
        self.__routeReferee = configs['amqp_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, configs['amqp_consume']);

        ## Credentials:
        self.__rabbitUser = configs['rabbitmq']['user'];
        self.__rabbitPass = configs['rabbitmq']['pass'];

        configs['amqp_publish']['user'] = self.__rabbitUser;
        configs['amqp_publish']['pass'] = self.__rabbitPass;

        ## Instance a new object to perform the publication of 'AMQP' messages.
        self.__publish=RabbitMQ_Publish(configs['amqp_publish']);

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = Database(configs['database']);


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

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        message = json.loads(message);

        ## Check if is a request received from players or a return from a divi-
        ## sions. The identifier is the properties.app_id.
        if properties.app_id == 'MCT_Referee':
            if self.__inspect_request(message) == 0:
                self.__recv_message_referee(message, properties.app_id);
        else:
            if self.__inspect_request(message) == 0:
                self.__send_message_referee(message, properties.app_id);

        return 0;



    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: receive message from referee.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ## @PARAM str  appId   == source app id.
    ##
    def __recv_message_referee(self, message, appId):
        ## LOG:
        logger.info('MESSAGE RETURNED OF REFEREE: %s', message);

        if message['retId'] == '':
            ## Remove the message (put previous) in the pending requests dicti-
            ## onary.
            valRet = self.__remove_query(message['reqId']);

            playerAddress = message['origAdd'];

        ## Here is make the request forward to player that will accept the req-
        ## quest.
        else:
            playerAddress = message['destAdd'];

        ## Create the configuration about the return message.This configuration
        ## will be used to send the messagem to apropriate player.
        config = {
            'identifier': AGENT_IDENTIFIER,
            'route'     : AGENT_ROUTE,
            'exchange'  : AGENT_EXCHANGE,
            'queue_name': AGENT_QUEUE,
            'address'   : playerAddress,
            'user'      : self.__rabbitUser,
            'pass'      : self.__rabbitPass
        };

        targetPublish = RabbitMQ_Publish(config); 
        targetPublish.publish(message, AGENT_ROUTE);

        del targetPublish;
        return 0;


    ##
    ## BRIEF: send message to the refereee.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ## @PARAM str  appId   == source app id.
    ##
    def __send_message_referee(self, message, appId):
       ## LOG:
       logger.info('MESSAGE SEND TO REFEREE: %s BY APP: %s', message, appId);

       ## The message can be a request for action or a response for action per-
       ## formed. Check the message type, if respId == '' is a request.
       if message['retId'] == '':

           ## Adds the message in the pending requests dictionary. If it is al-
           ## readyinserted does not perform the action.
           valRet=self.__append_query(appId, message['reqId'], message['code']);

       ## Send the message to MCT_Referee.
       self.__publish.publish(message, self.__routeReferee);

       return 0;


    ##
    ## BRIEF: stores the request identifier.
    ## ------------------------------------------------------------------------
    ## @PARAM str playerId  == identifier of the player.
    ## @PARAM str requestId == identifier of the request.
    ## @PARAM str actionId  == identifier of the action.
    ##
    def __append_query(self, playerId, requestId, actionId):
        ## 
        timeStamp = timeStamp = str(datetime.datetime.now());

        ## Check if the line that represent the request already in db. Perform
        ## a select.
        query  = "SELECT status FROM REQUEST WHERE ";
        query += "request_id='"    + str(requestId) + "' "
        query += "and player_id='" + str(playerId) + "'";
        valRet = [] or self.__dbConnection.select_query(query)

        ## Verifies that the request already present in the requests 'database'
        ## if not insert it.
        if valRet == [] or valRet[0][0] != 0:
            ## LOG:
            logger.info('MESSAGE PENDING: %s', requestId);

            ## Insert a line in table REQUEST from database mct. Each line mean
            ## a request finished or in execution.
            query  = "INSERT INTO REQUEST (";
            query += "player_id, ";
            query += "request_id, ";
            query += "action, ";
            query += "status, ";
            query += "timestamp_received";
            query += ") VALUES (%s, %s, %s, %s, %s)";
            value  = (playerId, requestId, actionId, 0, timeStamp);
            valRet = self.__dbConnection.insert_query(query, value)

            return 0;

        ## LOG:
        logger.info('MESSAGE ALREADY PENDING: %s (NOT INSERTED)', requestId);

        ## 
        return 1;


    ##
    ## BRIEF: remove the request identifier.
    ## ------------------------------------------------------------------------
    ## @PARAM str msgId == identifier of the request.
    ##
    def __remove_query(self, requestId):
        ## 
        timeStamp = timeStamp = str(datetime.datetime.now());

        ## Check if the line that represent the request already in db. Perform
        ## a select.
        query  = "SELECT player_id FROM REQUEST WHERE ";
        query += "request_id='" + str(requestId) + "' "
        valRet = [] or self.__dbConnection.select_query(query);

        try:
            query  = "UPDATE REQUEST SET ";
            query += "status=1, ";
            query += "timestamp_finished='" + str(timeStamp) + "' ";
            query += "WHERE ";
            query += "player_id='"  + str(valRet[0][0]) + "' and ";
            query += "request_id='" + str(requestId) + "'";
            valRet = self.__dbConnection.update_query(query);
        except:
            pass;
 
        ## LOG:
        logger.info('MESSAGE %s REMOVED FROM PENDING!', requestId);
        return 0;


    ##
    ## BRIEF: check if all necessary fields are in the request.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __inspect_request(self, request):
        ## TODO: DEFINR FORMATO!

        ## LOG:
        logger.info('INSPECT REQUEST!');
        return 0;
## END.







###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    ## LOG:
    logger.info('EXECUTION STARTED...');

    try:
        mct_dispatch = MCT_Dispatch();
        mct_dispatch.consume();

    except KeyboardInterrupt, error:
        pass;

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF.
