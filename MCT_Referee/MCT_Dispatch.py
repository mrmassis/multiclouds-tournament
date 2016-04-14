#!/usr/bin/env python


import ConfigParser;
import sys;
import json;

from lib.amqp import RabbitMQ_Publish, RabbitMQ_Consume;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE = '../mct_dispatch.ini';
PLAYER_FILE = '../players.ini';




###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Dispatch(RabbitMQ_Consume):

    """
    Dispatch to appropriate destinations requires received from players or divi
    sions.
    ---------------------------------------------------------------------------
    callback == method invoked when the pika receive a message.
    
    
    __recv_message_divisions == receive message from divisions.
    __send_message_divisions == sends the message to the appropriate divisions.
    __append_query           == stores the request identifier.
    __valid_request_send     == check if all necessary fields are in the reque
                                st from players.
    __valid_request_recv     == check if all necessary fields are in the reque
                                st from divisions.
    __get_divisions          == return the division than player belong.
    __get_configs            == obtain all configuration from conffiles.

    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __queueName       = None;
    __identifier      = None;
    __route           = None;
    __address         = None;
    __exchange        = None;
    __requestsPending = None;
    __divisions       = None;

    __configs         = None;
    __players         = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, cfgFile = 'mct_dispatch.ini'):
        self.__requestsPending = {};

        ## Obtain all configs parameters presents in the file and the players
        ## presente in the organizations:
        configs = self.__get_config(CONFIG_FILE);
        self.__players = self.__get_config(PLAYER_FILE);

        ##
        self.__routeReferee = configs['amqp_publish']['route'];

        ## Obtain all divisions defined in "MCT_Dispatch.ini" configure file .
        self.__divisions = [];
        for div in range(1, int(configs['main']['num_divisions']) + 1):
            self.__divisions.append(div);

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, configs['amqp_consume']);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publisher = RabbitMQ_Publish(configs['amqp_publish']);



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
        self.chn.basic_ack(method.delivery_tag);

        ## LOG:
        print '[LOG]: AMQP APP ID : ' + str(properties.app_id);

        message = json.loads(message);

        ## Check if is a request received from players or a return from a divi-
        ## sions. The identifier is the properties.app_id.
        if properties.app_id == 'MCT_Referee':
            #if self.__valid_request_recv(message) == 0:
                self.__recv_message_divisions(message, properties.app_id);
        else:
            #if self.__valid_request_send(message) == 0:
                self.__send_message_divisions(message, properties.app_id);

        return 0;



    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: receive message from divisions.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ## @PARAM str  appId   == source app id.
    ##
    def __recv_message_divisions(self, message, appId):

        ## Remove the message (put previous) in the pending requests dictionary
        valRet = self.__remove_query(message['msg_id']);

        ## LOG:
        print '[LOG] RETURN OF REFEERE: ' + str(message);

        ## Send to player the request confirmation:
        #self.__publisher.publish(message, appId);

        return 0;



    ##
    ## BRIEF: sends the message to the appropriate divisions.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ## @PARAM str  appId   == source app id.
    ##
    def __send_message_divisions(self, request, appId):

       ## LOG:
       print '[LOG] REQUEST RECEIVED: ' + str(request);

       ## Adds the message in the pending requests dictionary. If it is already
       ## inserted does not perform the action.
       valRet = self.__append_query(request['msg_id'], appId);

       if valRet == 0:

           ## It obtained the division that the player is classified.It is also
           ## performed to validate the player. 
           numDivision = self.__get_division(request);

           if numDivision != 0:
               print self.__routeReferee
               self.__publisher.publish(request, self.__routeReferee);
           else:
               print 'LOG: Invalid Division ...';

       return 0;



    ##
    ## BRIEF: stores the request identifier.
    ## ------------------------------------------------------------------------
    ## @PARAM str msgId == identifier of the request.
    ##
    def __append_query(self, msgId, appId):

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

        ## LOG:
        print '[LOG] removida a message com ID: '+ str(msgId) +' do pending!';

        ## Delete msgId element from a dictionary __requestsPending.
        self.__requestsPending.pop(msgId);
        return 0;


    ##
    ## BRIEF: check if all necessary fields are in the request from divisions.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __valid_request_recv(self, request):
        ## Verify other aspect from request.

        keywords = [
            'action',
            'player',
            'msg_id',
            'status'
        ];

        for key in keywords:
             if not request.has_key(key):
                print "LOG: missed field " + key;
                return 1;

        return 0;


    ##
    ## BRIEF: check if all necessary fields are in the request from players.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __valid_request_send(self, request):

        ## LOG:
        print '[LOG] Message: ' + str(request);

        ## Verifica os campos da mensagem:
        




        ## Verify other aspect from request.

        keywords = [
            'action',
            'player',
            'vmt_id',
            'msg_id',
            'div_id',
        ];

        for key in keywords:
             if not request.has_key(key):
                print "LOG: missed field " + key;
                return 1;

        return 0;


    ##
    ## BRIEF: return the division than player belong.
    ## ------------------------------------------------------------------------
    ## @PARAM player == player to analyze.
    ##
    def __get_division(self, request):

        if int(request['div_id']) in self.__divisions:
            return int(request['div_id']);

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
    daemon = MCT_Dispatch();
    daemon.consume();

## EOF.
