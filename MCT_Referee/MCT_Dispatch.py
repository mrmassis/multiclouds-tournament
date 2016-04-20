#!/usr/bin/env python


import ConfigParser;
import sys;
import json;
import datetime;

from lib.database import Database;
from lib.amqp     import RabbitMQ_Publish, RabbitMQ_Consume;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE      = '/etc/mct/mct_dispatch.ini';
AGENT_ROUTE      = 'mct_agent';
AGENT_IDENTIFIER = 'MCT_Dispatch';
AGENT_EXCHANGE   = 'mct_agent_exchange';
AGENT_QUEUE      = 'agent';




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
    __valid_request        == check if all necessary fields are in request.
    __get_configs          == obtain all configuration from conffiles.

    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __publish         = None;
    __divisions       = [];
    __configs         = None;
    __dbConnection    = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        configs = self.__get_config(CONFIG_FILE);

        ## Get which 'route' is used to deliver the message to the MCT_Referee.
        self.__routeReferee = configs['amqp_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, configs['amqp_consume']);

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
        ## LOG:
        print '[LOG]: AMQP APP ID : ' + str(properties.app_id);

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        message = json.loads(message);

        ## Check if is a request received from players or a return from a divi-
        ## sions. The identifier is the properties.app_id.
        if properties.app_id == 'MCT_Referee':
            if self.__valid_request(message) == 0:
                self.__recv_message_referee(message, properties.app_id);
        else:
            if self.__valid_request(message) == 0:
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
        print '[LOG]: RETURN OF REFEERE: ' + str(message);


        if message['retId'] == '':
            ## Remove the message (put previous) in the pending requests dicti-
            ## onary.
            valRet = self.__remove_query(message['reqId']);

            playerAddress = message['origAdd'];
        else:
            playerAddress = message['destAdd'];

        ## Create the configuration about the return message.This configuration
        ## will be used to send the messagem to apropriate player.
        config = {
            'identifier': AGENT_IDENTIFIER,
            'route'     : AGENT_ROUTE,
            'exchange'  : AGENT_EXCHANGE,
            'queue_name': AGENT_QUEUE,
            'address'   : playerAddress 
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
       print '[LOG]: REQUEST RECEIVED: ' + str(message);

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
            print '[LOG]: MESSAGE PENDING: ' + str(requestId);

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
        print '[LOG]: MESSAGE JAH PRESENTE: NAO INSERIDA!'

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

        query  = "UPDATE REQUEST SET ";
        query += "status=1, ";
        query += "timestamp_finished='" + str(timeStamp) + "' ";
        query += "WHERE ";
        query += "player_id='"  + str(valRet[0][0]) + "' and ";
        query += "request_id='" + str(requestId) + "'";
        valRet = self.__dbConnection.update_query(query);

        ## LOG:
        print '[LOG]: MESSAGE ID: '+ str(requestId) +' REMOVED FROM PENDING!';

        return 0;


    ##
    ## BRIEF: check if all necessary fields are in the request.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __valid_request(self, request):
        ## TODO: DEFINR FORMATO!

        ## LOG:
        print '[LOG]: DEFINIR FORMATO!';
        return 0;


    ##
    ## BRIEF: obtain all configuration from conffiles.
    ## ------------------------------------------------------------------------
    ## @PARAM str cfgFile == conffile name.
    ##
    def __get_config(self, cfgFile):
       cfg = {};

       config = ConfigParser.ConfigParser();
       config.readfp(open(cfgFile));

       for section in config.sections():
           cfg[section] = {};

           for option in config.options(section):
               cfg[section][option] = config.get(section, option);

       return cfg;
## END.







###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    try:
        ## LOG:
        print '[LOG]: EXECUTION STARTED....';

        daemon = MCT_Dispatch();
        daemon.consume();

    except KeyboardInterrupt, error:
        ## LOG:
        print '[LOG]: EXECUTION FINISHED...';

    sys.exit(0);
## EOF.
