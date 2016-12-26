#!/usr/bin/env python


import sys;
import json;
import time;
import logging;
import logging.handlers;
import pika;
import datetime;

from mct.lib.utils    import *;
from mct.lib.emulator import MCT_Emulator;
from mct.lib.amqp     import RabbitMQ_Publish, RabbitMQ_Consume;
from mct.lib.database import MCT_Database;
from mct.lib.registry import MCT_Registry;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE  = '/etc/mct/mct-simulation.ini';
LOG_NAME     = 'MCT_Agent_Simulation';
LOG_FORMAT   = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME = '/var/log/mct/mct_agent_simulation.log';
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
    __routeInt     = None;
    __routeExt     = None;
    __publishInt   = None;
    __publishExt   = None;
    __my_ip        = None;
    __cloud        = None;
    __cloudType    = None;
    __dbConnection = None;
    __emulated     = None;
    __emulator     = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, config):

        ## Local address:
        self.__my_ip = config['main']['my_ip'];

        ## Get which route is used to deliver the msg to the 'correct destine'.
        self.__routeExt = config['amqp_external_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, config['amqp_consume']);

        ### Credentials:
        config['amqp_external_publish']['user'] = config['rabbitmq']['user'];
        config['amqp_external_publish']['pass'] = config['rabbitmq']['pass'];

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publishExt = RabbitMQ_Publish(config['amqp_external_publish']);

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = MCT_Database(config['database']);

        ## Object that represet the cloud API emulator:
        self.__cloud = MCT_Emulator();


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
        if properties.app_id == DISPATCH_NAME:
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

        ## Publish the message to MCT_Dispatch via AMQP. The MCT_Dispatch is in
        ## the remote server. 
        valRet = self.__publishExt.publish(message, self.__routeExt);

        if valRet == False:
            ## LOG:
            logger.error("IT WAS NOT POSSIBLE TO SEND THE MSG TO DISPATCH!");
        else:
            ## LOG:
            logger.info ('MESSAGE SENT TO DISPATCH!');
      
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
        if message['destAdd'] != '':

            ## LOG:
            logger.info('PROCESSING REQUEST!');

            ## Select the appropriate action (create instance, delete instance,
            ## suspend instance e resume instance): 
            ## Create:
            if   message['code'] == CREATE_INSTANCE:
                status = self.__create_server(message);

            ## Delete:
            elif message['code'] == DELETE_INSTANCE:
                status = self.__delete_server(message);

            ## The MCT_Agent support more than one cloud framework.So is neces-
            ## sary prepare the return status to a generic format. Send back to
            ## dispatch the return for the request.
            message['status'] = self.__convert_status(status, message['code']); 

            ## Return data to MCT_Dispatch.
            self.__publishExt.publish(message, self.__routeExt);

        ## Return from a action:
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
        query  = "INSERT INTO REQUEST (player_id, request_id, status, message) ";
        query += "VALUES (%s,%s,%s,%s)";
        value  = (str(message['playerId']), 
                  str(message['reqId'   ]), 
                  int(message['status'  ]),
                  str(message['data'    ]));

        valret = self.__dbConnection.insert_query(query, value);


    ##
    ## BRIEF: create localy a new server. 
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __create_server(self, msg):

        status = 'ERROR';

        ## Check if is possible create the new server (vcpu, memory, and disk).
        query = "SELECT * FROM RESOURCES player_id='" + msg['playerId'] + "'";

        dataReceived = [] or self.__dbConnection.select_query(query)[0];

        if dataReceived != []:

            ## Get the index that meaning the flavors.(vcpus, memory, and disk).
            i =FLV_NAME.keys()[FLV_NAME.values().index(msg['data']['flavor'])];

            newVcpuUsed = int(dataReceived[2]) + int(CPU_INFO[i]);
            newMemoUsed = int(dataReceived[4]) + int(MEN_INFO[i]);
            newDiskUsed = int(dataReceived[6]) + int(DSK_INFO[i]);

            ## Check if there are 'avaliable' resources to accept the instance.
            if  newVcpuUsed =< int(dataReceived[1]) and 
                newMemoUsed =< int(dataReceived[3]) and 
                newDiskUsed =< int(dataReceived[5]):

                ## Update the specific entry in dbase with new resource values.
                query  = "UPDATE RESOURCES SET "
                query += "vcpus_used='"      + str(newVcpuUsed) + "',";
                query += "memory_mb_used='"  + str(newMemoUsed) + "',";
                query += "local_gb_used='"   + str(newDiskUsed) + "' ";
                query += "WHERE player_id='" + msg['playerId']  + "'" ;

                valRet = self.__dbConnection.update_query(query);

                ## Obtain a new hash to set the reqId:
                destId = self.__create_index(); 

                ## Insert in the MAP table the origin uuid (player source) and
                ## the local instance uuuid. Here is where the data about run-
                ## ning instances:
                self.__set_map_inst_id(destId, message['reqId']);

                status = 'ACTIVE';

        return status;


    ##
    ## BRIEF: delete localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __delete_server(self, msg):

        ## Check if is possible create the new server (vcpu, memory, and disk).
        query = "SELECT * FROM RESOURCES player_id='" + msg['playerId'] + "'";

        dataReceived = [] or self.__dbConnection.select_query(query)[0];

        if dataReceived != []:

            ## Get the index that meaning the flavors.(vcpus, memory, and disk).
            i =FLV_NAME.keys()[FLV_NAME.values().index(msg['data']['flavor'])];

            newVcpuUsed = int(dataReceived[2]) - int(CPU_INFO[i]);
            newMemoUsed = int(dataReceived[4]) - int(MEN_INFO[i]);
            newDiskUsed = int(dataReceived[6]) - int(DSK_INFO[i]);

            ## Update the specific entry in database with new resource values.
            query  = "UPDATE RESOURCES SET "
            query += "vcpus_used='"      + str(newVcpuUsed) + "',";
            query += "memory_mb_used='"  + str(newMemoUsed) + "',";
            query += "local_gb_used='"   + str(newDiskUsed) + "' ";
            query += "WHERE player_id='" + msg['playerId']  + "'" ;

            valRet = self.__dbConnection.update_query(query);

            ## Delete the instance from map ID table:
            self.__get_map_inst_id(message['reqId'], True);

        return 'HARD_DELETED';


    ##
    ## BRIEF: check if all necessary fields are in the request.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __inspect_request(self, request):
        return 0;


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
    ## BRIEF: create a new index based in a hash.
    ## ------------------------------------------------------------------------
    ##
    def __create_index(self):

        ## Use FIPS SHA security algotirh sha512() to create a SHA hash object.
        newHash = hashlib.sha512();

        ## Update the hash object with the string arg. Repeated calls are equi-
        ## valent to a single call with the concatenation of all the arguments:
        newHash.update(str(time.time()));

        ## Return a hash with ten position:
        return newHash.hexdigest()[:10];


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

    config = get_configs(CONFIG_FILE);

    try:
        ## Case this agent is virtual (to emulate), open the file with vagents
        ## specification.
        for i in range(int(config['main']['vplayers'])):
            vName = 'vplayer' + str(i);

            ## Get configuration options to the virtual player (amqp,quote etc)
            vCfg = config[vName];
    
            try:
                sAddr = vCfg['authenticate_address'];
                sPort = vCfg['authenticate_port'   ];
                aAddr = vCfg['agent_address'       ];
                aName = vCfg['name'                ];

                mct_registry = MCT_Registry(aAddr, aName, sAddr, sPort);
                mct_registry.registry();
            except:
                pass;

        mct = MCT_Agent(config);
        mct.consume();

    except KeyboardInterrupt:
        pass;

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF
