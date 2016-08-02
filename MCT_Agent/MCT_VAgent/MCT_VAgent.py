#!/usr/bin/env python


import sys;
import json;
import time;
import logging;
import logging.handlers;
import pika;
import datetime;

from lib.utils         import *;
from lib.amqp          import RabbitMQ_Publish, RabbitMQ_Consume;
from lib.database      import MCT_Database;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE  = '/etc/mct/mct_vagent.ini';
LOG_NAME     = 'MCT_Agent';
LOG_FORMAT   = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME = '/var/log/mct/mct_agent.log';
DISPATCH_NAME= 'MCT_Dispatch';





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
    Class MCT_Agent. 
    ---------------------------------------------------------------------------
    callback == method invoked when the pika receive a message.
    
    __recv_message_referee == receive message from referee.
    __send_message_referee == send message to referee.
    __inspect_request      == check if all necessary fields are in request.

    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __route        = None;
    __publish      = None;
    __dbConnection = None;
    __myIp         = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        config = get_configs(CONFIG_FILE);

        ## Get the local address.
        self.__myIp = config['main']['my_ip']; 

        ## Get which route is used to deliver the msg to the 'correct destine'.
        self.__route = config['amqp_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, config['amqp_consume']);

        ### Credentials:
        config['amqp_publish']['user'] = config['rabbitmq']['user'];
        config['amqp_publish']['pass'] = config['rabbitmq']['pass'];

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish = RabbitMQ_Publish(config['amqp_publish']);

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = MCT_Database(config['database']);


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

        self.__recv_message_dispatch(message, properties.app_id);
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: receive message from MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ## @PARAM str appId    == application identifier.
    ##
    def __recv_message(self, message, appId):

        ## LOG:
        logger.info('MESSAGE RETURNED OF %s DISPATCH %s', appId, message);

        ## In this case, the MCT_Agent received actions to be performed locally.
        if message['origAdd'] != self.__myIp and message['destAdd'] != '':

            ## LOG:
            logger.info('PROCESSING REQUEST!');

            ## Select the appropriate action (create instance, delete instance,
            ## suspend instance e resume instance): 
            ## Create:
            if   message['code'] == CREATE_INSTANCE:
                status = self.__create_vserver(message);

            ## Delete:
            elif message['code'] == DELETE_INSTANCE:
                status = self.__delete_vserver(message);

            ## Suspend:
            elif message['code'] == SUSPND_INSTANCE:
                status = self.__suspnd_vserver(message);

            ## Resume:
            elif message['code'] == RESUME_INSTANCE:
                status = self.__resume_vserver(message);

            ## The MCT_Agent support more than one cloud framework.So is neces-
            ## sary prepare the return status to a generic format. Send back to
            ## dispatch the return for the request.
            message['status'] = self.__convert_status(status, message['code']); 

            ## Return data to MCT_Dispatch.
            self.__publish.publish(message, self.__route);
        else:
            ## Update the database:
            self.__update_database(message);

        return 0;


    ##
    ## BRIEF: updata database with return value.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __update_database(self, message):
        if message['code'] == SETINF_RESOURCE: 
            return 0;

        ## Insert the message received into the database.
        query  ="INSERT INTO REQUEST (player_id, request_id, status, message) ";
        query +="VALUES (%s, %s,%s,%s)";
        value  =(message['playerId'], 
                 message['reqId'   ], 
                 message['status'  ], 
                 message['data'    ]);

        valret = self.__dbConnection.insert_query(query, value);


    ##
    ## BRIEF: create localy a new server. Receive the message, extract the ser-
    ##        ver information (name, image, flavor, and net) and send to frame-
    ##        work. So, wait return and check the return status. At finish, if
    ##        the status == ACTIVE, make a mapping between id received and the
    ##        local ID. At last, send back the status.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __create_vserver(self, message):
        return 'NOT_IMPLEMENTED';


    ##
    ## BRIEF: delete localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __delete_vserver(self, message):
        return 'NOT_IMPLEMENTED';


    ##
    ## BRIEF: suspnd localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __suspnd_vserver(self, message):
        return 'NOT_IMPLEMENTED';


    ##
    ## BRIEF: resume localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __resume_vserver(self, message):
        return 'NOT_IMPLEMENTED';


    ##
    ## BRIEF: convert de oper status to a generic format.
    ## ------------------------------------------------------------------------
    ## @PARAM dict status == original status.
    ## @PARAM dict conde  == operation code.
    ##
    def __convert_status(self, status, code):

        if self.__cloudType == 'openstack':
            ## First colum is an operation {1 = create, 2 = delete, 3 = (...)}.
            genericStatus = {
                CREATE_INSTANCE : { 'NOSTATE':0, 'ERROR':0, 'ACTIVE':1},
                DELETE_INSTANCE : { 'NOSTATE':0, 'ERROR':0, 'HARD_DELETED':1,'DELETED':1},
                SUSPND_INSTANCE : { 'NOSTATE':0, 'ERROR':0, 'SUSPENDED'   :1},
                RESUME_INSTANCE : { 'NOSTATE':0, 'ERROR':0, 'ACTIVE'      :1}
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
        query += ") VALUES (%s, %s, %s, %s)";
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
                query  = "DELETE FROM MAP WHERE uuid_src='" + origId + "'";

                valRet = self.__dbConnection.delete_query(query); 

        return destId;
## END.







###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    ## LOG:
    logger.info('EXECUTION STARTED...');

    try:
        mct = MCT_Agent();
        mct.consume();
    except KeyboardInterrupt:
        pass;

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF
