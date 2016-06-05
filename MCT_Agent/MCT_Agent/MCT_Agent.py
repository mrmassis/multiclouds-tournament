#!/usr/bin/env python


import ConfigParser;
import sys;
import json;
import time;
import logging;
import logging.handlers;
import pika;
import datetime;

from lib.openstack_API          import MCT_Openstack_Nova;
from lib.amqp                   import RabbitMQ_Publish, RabbitMQ_Consume;
from nova.virt.mct.lib.database import MCT_Database;








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
    __routeInt     = None;
    __routeExt     = None;
    __publishInt   = None;
    __publishExt   = None;
    __my_ip        = None;
    __cloud        = None;
    __cloudType    = None;
    __dbConnection = None;


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

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = MCT_Database(config['database']);

        ## Check the type of framework utilized to build the cloud.Intance the
        ## correct API.
        self.__cloudType = config['cloud_framework']['type'];

        if self.__cloudType == 'openstack':

            name = config['cloud_framework']['name'];
            pswd = config['cloud_framework']['pass'];
            auth = config['cloud_framework']['auth'];
            proj = config['cloud_framework']['proj'];

            self.__cloud = MCT_Openstack_Nova(name, pswd, auth, proj);


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
            ## Create:
            if message['code'] == 1:

                vmsL = message['data']['name'  ];
                imgL = message['data']['image' ];
                fvlL = message['data']['flavor'];
                netL = 'fake-net';

                status = self.__cloud.create_instance(vmsL, imgL, flvL, netL);

                ## Insert in the MAP_UUID table the origin uuid (player source)
                ## and the local instance uuuid.
                self.__set_map_inst_id(destId, message['data']['reqId']);

            ## Delete:
            elif message['code'] == 2:
                instId =self.__get_map_inst_id(message['data']['reqId'],True);
                status =self.__cloud.delete_instance(instId);

            ## Suspend:
            elif message['code'] == 3:
                instId =self.__get_map_inst_id(message['data']['reqId']);
                status =self.__cloud.suspend_instance(instId);

            ## Resume:
            elif message['code'] == 4:
                instId =self.__get_map_inst_id(message['data']['reqId']);
                status =self.__cloud.resume_instance(instId);

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

        if self.__cloudType == 'openstack':
            genericStatus = {
                1 : { 'ERROR':0, 'ACTIVE'      :1},
                2 : { 'ERROR':0, 'HARD_DELETED':1},
                3 : { 'ERROR':0, 'SUSPENDED'   :1},
                4 : { 'ERROR':0, 'ACTIVE'      :1}
            }

        return genericStatus[code][status];


    ##
    ## Brief: create a map between two uuid.
    ## ------------------------------------------------------------------------
    ## @PARAM str destId == local uuid.
    ## @PARAM str origId == origin uuid.
    ##
    def __set_map_inst_id(self, destId, origId):
        ## 
        timeStamp = str(datetime.datetime.now());

        query  = "INSERT INTO MAP (";
        query += "uuid_src, ";
        query += "uuid_dst, ";
        query += "type_obj, ";
        query += "date";
        query += ") VALUES (%s, %s, %s, %s, %s)";
        value  = (origId, destId, 'instance', timeStamp);

        valRet = self.__dbConnection.insert_query(query, value);

        return 0;

    ##
    ## Brief: get the local uuid from object.
    ## ------------------------------------------------------------------------
    ## @PARAM str  origId == origin uuid.
    ## @PARAM bool delete == check if is to delete entry.
    ##
    def __get_map_inst_id(self, origId, delete=False):
        destId = '';

        ## Mount the select query: 
        dbQuery  = "SELECT uuid_dst FROM MAP WHERE ";
        dbQuery += "uuid_src='" + origId + "'";

        dataReceived = [] or self.__dbConnection.select_query(dbQuery);

        if dataReceived != []:
            destId = dataReceived[0][0];

            if delete:
                ## Delete the correspondent entry:
                query  = "DELETE uuid_src FROM MAP WHERE "
                query += "uuid_src='" + origId + "'";

                valRet = self.__dbConnection.delete_query(query); 

        return dstId;


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
