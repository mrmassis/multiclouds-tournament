#!/usr/bin/env python


import pika;
import time;
import sys;
import os;
import datetime;
import json;
import logging;
import logging.handlers;

from multiprocessing     import Process, Queue, Lock;
from mct.lib.scheduller  import *;
from mct.lib.amqp        import RabbitMQ_Publish, RabbitMQ_Consume;
from mct.lib.utils       import *;
from mct.lib.database    import MCT_Database;





###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE   = '/etc/mct/mct-referee.ini';
LOG_NAME      = 'MCT_Security';
LOG_FORMAT    = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME  = '/var/log/mct/mct_security.log';








###############################################################################
## LOG                                                                       ##
###############################################################################
## Create a handler and define the output filename and the max size and max nun
## ber of the files (1 mega = 1048576 bytes).
handler= logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                              maxBytes=10485760,
                                              backupCount=100);

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
class MCT_Security(RabbitMQ_Consume):

    """
    Class MCT_Security: .
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    ** callback       == waiting for requests.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __db    = None;
    __print = None;
    __cfg   = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM dict cfg    == dictionary with configurations about MCT_Agent.
    ## @PARAM obj  logger == logger object.
    ##
    def __init__(self, cfg, logger):

        ## Obtain the configuration fields with 'appropriate' format and types.
        self.__get_configurations(cfg);

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(self.__cfg['print'], logger);

        ## LOG:
        self.__print.show('##### INITIALIZE MCT_REFEREE #####', 'I');

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, self.__cfg['amqp_consume']);

        # Instantiates an object to perform the publication of AMQP messages.
        self.__publish = RabbitMQ_Publish(self.__cfg['amqp_publish']);

        ## Intance a new object to handler all operation in the local database
        self.__db = MCT_Database(self.__cfg['database']);


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
        appId = properties.app_id;

        ## LOG:
        self.__print.show('MESSAGE RECEIVED: ' + message + ' Id: '+ appId,'I');

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        ## The json.loads translate a string containing JSON data into a Python
        ## dictionary format.
        message = json.loads(message);
 
        ## Check the messsge received.Verify if all fields are presents and are
        ## in correct form.
        valRet = self.__inspect_request(message);

        if valRet == 0:

            ## ------------------------------------------------------------- ##
            ## REGISTRY A NEW PLAYER                                         ##
            ## ------------------------------------------------------------- ##
            if   int(message['code']) == REGISTRY:

                ## LOG:
                self.__print.show('REGISTRY' ,'I');

                message = self.__registry(message);
 
            ## ------------------------------------------------------------- ##
            ## GET AUTHORIZATION TO ACCESS RESOUCES                          ##
            ## ------------------------------------------------------------- ##
            elif int(message['code']) == RESOURCE:

                ## LOG:
                self.__print.show('RESOURCE' ,'I');

                message = self.__resource(message);

            ## ------------------------------------------------------------- ##
            ## OBTAIN A NEW TOKEN                                            ##
            ## ------------------------------------------------------------- ##
            elif int(message['code']) == GETTOKEN:

                ## LOG:
                self.__print.show('GETTOKEN' ,'I');

                message = self.__gettoken(message);

        else:
            ## Error parse:
            message['status'] = MESSAGE_PARSE_ERROR;

        self.__publish.publish(message, self.__cfg['route']);
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: registry a new player.
    ## ------------------------------------------------------------------------
    ## @PARAM message == message data.
    ##
    def __registry(self, message):
        return message;


    ##
    ## BRIEF: obtain the autorization to access the resources.
    ## ------------------------------------------------------------------------
    ## @PARAM message == message data.
    ##
    def __resource(self, message):
        return message;


    ##
    ## BRIEF: obtain a token to player.
    ## ------------------------------------------------------------------------
    ## @PARAM message == messagem data.
    ##
    def __gettoken(self, message):
        return message;


    ##
    ## BRIEF: obtain the configuration in appropriate types.
    ## ------------------------------------------------------------------------
    ## @PARAM configDivisions == dictionary with raw values.
    ##
    def __get_configurations(self, configDivisions):

        ## Obtain the route name to publish messages (return) to MCT_Dispatch. 
        f1 = configDivisions['amqp_publish']['route'];

        ## Obtain all credentials to access the database. The creditials inclu
        ## de user, pass, and address.
        f2 = configDivisions['database'];
        
        ## Check the directive thar declares if the print will be in screen or
        ## in logger (is possible set to both).
        f3 = configDivisions['main']['print'];

        ## Obtain the informations about the protocol AMQ. The dictionary con-
        ## tain info about publish and consume.
        f4 = configDivisions['amqp_publish'];
        f5 = configDivisions['amqp_consume'];

        self.__cfg = {
            'route'        : f1,
            'database'     : f2,
            'print'        : f3,
            'amqp_publish' : f4,
            'amqp_consume' : f5
        };

        return 0;

## END.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    ## Get all configs parameters presents in the config file localized in
    ## CONFIG_FILE path.
    cfg = get_configs(CONFIG_FILE);

    try:
        mctReferee = MCT_Security(cfg, logger);
        mctReferee.consume();

    except KeyboardInterrupt, error:
        pass;

    sys.exit(0);
## EOF.

