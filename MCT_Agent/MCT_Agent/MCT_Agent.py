#!/usr/bin/env python


import ConfigParser;
import sys;
import json;
import time;
import logging;
import logging.handlers;
import pika;


from lib.openstack_API import MCT_Openstack_Nova;
from lib.amqp          import RabbitMQ_Publish, RabbitMQ_Consume;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE  = '/etc/mct/mct_agent.ini';
LOG_NAME     = 'MCT_Agent';
LOG_FORMAT   = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME = '/var/log/mct/mct_agent.log';







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
class MCT_Agent(RabbitMQ_Consume):

    """
    
    ---------------------------------------------------------------------------
    callback == method invoked when the pika receive a message.
    
    __recv_message_referee == receive message from referee.
    __send_message_referee == send message to referee.
    __inspect_request      == check if all necessary fields are in request.

    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __routeInt   = None;
    __routeExt   = None;
    __publishInt = None;
    __publishExt = None;
    __my_ip      = None;
    __cloud      = None;
    __cloudType  = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        config = self.__get_config(CONFIG_FILE);

        ## Local address:
        self.__my_ip = config['main']['my_ip'];

        ## Get which route is used to deliver the msg to the 'correct destine'.
        self.__routeInt = config['amqp_internal_publish']['route'];
        self.__routeExt = config['amqp_external_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, config['amqp_consume']);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publishInt = RabbitMQ_Publish(config['amqp_internal_publish']);
        self.__publishExt = RabbitMQ_Publish(config['amqp_external_publish']);

        ## Check the type of framework utilized to build the cloud.Intance the
        ## correct API.
        self.__cloudType = config['cloud_framework']['type'];

        if self.__cloudType == 'openstack';
            name = config['cloud_framework']['name'];
            pass = config['cloud_framework']['pass'];
            auth = config['cloud_framework']['auth'];
            proj = config['cloud_framework']['proj'];

            self.__cloud = MCT_Openstack_Nova(name,pass,auth,proj);


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

        ## Convert the json format to a structure than can handle by the python
        message = json.loads(message);

        ## Check if is a request received from players or a return from a divi-
        ## sions. The identifier is the properties.app_id.
        if properties.app_id == 'MCT_Dispatch':
            if self.__inspect_request(message) == 0:
                self.__recv_message_dispatch(message, properties.app_id);
        else:
            if self.__inspect_request(message) == 0:
                self.__send_message_dispatch(message, properties.app_id);

        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: send message to MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __send_message_dispatch(self, message, appId):

        ## LOG:
        logger.info('MESSAGE SEND TO DISPATCH: %s', message);

        ## Publish the message to MCT_Dispatch via AMQP. 
        self.__publishExt.publish(message, self.__routeExt);
        return 0;


    ##
    ## BRIEF: receive message from MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __recv_message_dispatch(self, message, appId):

        ## LOG:
        logger.info('MESSAGE RETURNED OF %s REFEREE: %s', appId, message);

        ## In this case, the MCT_Agent received actions to be performed locally.
        if message['origAdd'] != self.__my_ip and message['destAdd'] != '':
            ## LOG:
            logger.info('PROCESSING REQUEST!');

            ## Select the appropriate action (create instance, delete instance,
            ## suspend instance e resume instance): 
            if message['code'] == 1:

                vmsL = message['data']['name'  ];
                imgL = message['data']['image' ];
                fvlL = message['data']['flavor'];
                netL = 'fake-net';

                status = self.__cloud.create_instance(vmsL, imgL, flvL, netL):

            elif message['code'] == 2:
                status =  self.__cloud.delete_instance(message['data']['id']);

            elif message['code'] == 3:
                status =  self.__cloud.suspend_instance(message['data']['id']);

            elif message['code'] == 4:
                status =  self.__cloud.resume_instance(message['data']['id']);

            ## --
            ## The MCT_Agent support more than one cloud framework.So is neces-
            ## sary prepare the return status to a generic format;
            message['status'] = self.__convert_status(status, message['code']); 

            self.__publishExt.publish(message, self.__routeExt);
        else:
            self.__publishInt.publish(message, self.__routeInt);

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


    ##
    ## BRIEF: convert de oper status to a generic format.
    ## ------------------------------------------------------------------------
    ## @PARAM dict status == original status.
    ## @PARAM dict conde  == operation code.
    ##
    def __convert_status(self, status, code):

        if self.__cloudType == 'openstack';
            ## TODO:
            genericStatus = {
                1 : { '' : 0,    },
                2 : { '' : 0,    },
                3 : { '' : 0,    },
                4 : { '' : 0,    }
            }

        return newStatus = genericStatus[code][status];


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
    ## LOG:
    logger.info('EXECUTION STARTED...');

    mct = MCT_Agent();
    mct.consume();

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF
