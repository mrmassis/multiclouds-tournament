#!/usr/bin/env python


import ConfigParser;
import sys;
import json;

from lib.amqp import RabbitMQ_Publish, RabbitMQ_Consume;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE = '/etc/mct/mct_dispatch.ini';




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
    __requestsPending = {};
    __divisions       = [];
    __configs         = None;


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

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish=RabbitMQ_Publish(configs['amqp_publish']);



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
    ## BRIEF: receive message from refereee.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ## @PARAM str  appId   == source app id.
    ##
    def __recv_message_referee(self, message, appId):
        ## LOG:
        print '[LOG]: RETURN OF REFEERE: ' + str(message);

        ## Remove the message (put previous) in the pending requests dictionary.
        valRet = self.__remove_query(message['msg_id']);

        ## TODO: obter info do player.
        ## Send to player the request confirmation:
        #self.__publish.publish(message, appId);

        return 0;


    ##
    ## BRIEF: send message to the refereee.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ## @PARAM str  appId   == source app id.
    ##
    def __send_message_referee(self, request, appId):
       ## LOG:
       print '[LOG]: REQUEST RECEIVED: ' + str(request);

       ## Adds the message in the pending requests dictionary. If it is already
       ## inserted does not perform the action.
       valRet = self.__append_query(request['msg_id'], appId);

       if valRet == 0:
           self.__publish.publish(request, self.__routeReferee);

       return 0;


    ##
    ## BRIEF: stores the request identifier.
    ## ------------------------------------------------------------------------
    ## @PARAM str msgId == identifier of the request.
    ##
    def __append_query(self, msgId, appId):

        #+--------------------+------------+------+-----+----------------+
        #| Field              | Type       | Null | Key | Extra          |
        #+--------------------+------------+------+-----+----------------+
        #| id                 | int(11)    | NO   | PRI | auto_increment |
        #| player_id          | int(11)    | NO   | MUL |                |
        #| request_id         | int(11)    | NO   |     |                |
        #| type               | int(11)    | NO   |     |                |
        #| status             | tinyint(1) | NO   |     |                |
        #| timestamp_received | timestamp  | YES  |     |                |
        #| timestamp_finished | timestamp  | YES  |     |                |
        #+--------------------+------------+------+-----+----------------+

        ## Verifies that the request already present in the requests dictionary
        ## if not insert it.
        if not self.__requestsPending.has_key(msgId):
            ## LOG:
            print '[LOG]: MESSAGE PENDING: ' + str(msgId);
            self.__requestsPending[msgId] = appId;
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
    def __remove_query(self, msgId):
        ## Delete msgId element from a dictionary __requestsPending.
        self.__requestsPending.pop(msgId);

        ## LOG:
        print '[LOG]: MESSAGE ID: '+ str(msgId) +' REMOVED FROM PENDING!';

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
