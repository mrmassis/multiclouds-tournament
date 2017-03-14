#!/usr/bin/env python


import sys;
import json;
import time;
import logging;
import logging.handlers;
import pika;
import datetime;

from mct.lib.utils               import *;
from mct.lib.openstack           import MCT_Openstack_Nova;
from mct.lib.amqp                import RabbitMQ_Publish, RabbitMQ_Consume;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy, Map, Instances, Request ;
from mct.lib.registry            import MCT_Registry;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE  = '/etc/mct/mct-agent.ini';
LOG_NAME     = 'MCT_Agent';
LOG_FORMAT   = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME = '/var/log/mct/mct_agent.log';
DISPATCH_NAME= 'MCT_Dispatch';
NET_NAME     = 'demo-net';







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
    __db           = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ## BRIEF: initialize the agent.
    ## ------------------------------------------------------------------------
    ## @PARAM cfg       == player's configuration.
    ## @PARAM authToken == token to authentication.
    ##
    def __init__(self, config, authToken):

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(config['main']['print'], logger);

        ## Local address:
        self.__my_ip = config['main']['agent_address'];

        ## Get which route is used to deliver the msg to the 'correct destine'.
        self.__routeExt = config['amqp_external_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, config['amqp_consume']);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publishExt = RabbitMQ_Publish(config['amqp_external_publish']);

        ## Intance a new object to handler all operation in the local database.
        self.__db = MCT_Database_SQLAlchemy(config['database']);

        ## Setting the player's authentication token:
        self.__authToken = authToken;

        ## Check the type of framework utilized to build the cloud.Intance the
        ## correct API.
        self.__cloudType = config['cloud_framework']['type'];

        if   self.__cloudType == 'openstack':
            self.__cloud = MCT_Openstack_Nova(config['cloud_framework']);

        ## LOG:
        self.__print.show("\n###### START MCT_AGENT ######\n",'I');


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
        self.__print.show('MESSAGE TO DISPATCH ' + str(message), 'I');

        ##
        ## TODO: check authToken to know if the player has permission grant!!!!
        ##

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
        self.__print.show('MESSAGE RETURNED FROM DISPATCH: '+str(message), 'I');

        ## In this case, the MCT_Agent received actions to be performed locally.
        if message['origAddr'] != self.__my_ip and message['destAddr'] != '':

            ## LOG:
            self.__print.show('PROCESSING REQUEST!', 'I');

            ## Select the appropriate action (create instance, delete instance,
            ## suspend instance e resume instance): 
            ## Create:
            if   message['code'] == CREATE_INSTANCE:
                status = self.__create_server(message);

            ## Delete:
            elif message['code'] == DELETE_INSTANCE:
                status = self.__delete_server(message);

            ## Suspend:
            elif message['code'] == SUSPND_INSTANCE:
                status = self.__suspnd_server(message);

            ## Resume:
            elif message['code'] == RESUME_INSTANCE:
                status = self.__resume_server(message);

            ## The MCT_Agent support more than one cloud framework.So is neces-
            ## sary prepare the return status to a generic format. Send back to
            ## dispatch the return for the request.
            message['status'] = self.__convert_status(status, message['code']); 

            ## LOG:
            self.__print.show('RETURN TO DISPATCH!', 'I');

            ## Return data to MCT_Dispatch.
            self.__publishExt.publish(message, self.__routeExt);

        ## Return from a action:
        else:
            ## LOG:
            self.__print.show('SEND TO DRIVE!', 'I');

            ## Update the database:
            self.__update_database(message);

        return 0;


    ##
    ## BRIEF: updata database with return value.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __update_database(self, message):

        ## LOG:
        self.__print.show('UPDATE DATABASE ' + str(message), 'I');

        if message['code'] == SETINF_RESOURCE: 
            return 0;

        ## LOG:
        self.__print.show('UPDATE DATABASE!', 'I');

        ## Insert the message received into the database.
        request = Request();

        request.player_id  = str(message['playerId']);
        request.request_id = str(message['reqId'   ]);
        request.action     = int(message['code'    ]);
        request.status     = int(message['status'  ]);
        request.message    = str(message['data'    ]);

        valRet = self.__db.insert_reg(request);

        ## LOG:
        self.__print.show('UPDATED!', 'I');


    ##
    ## BRIEF: create localy a new server. Receive the message, extract the ser-
    ##        ver information (name, image, flavor, and net) and send to frame-
    ##        work. So, wait return and check the return status. At finish, if
    ##        the status == ACTIVE, make a mapping between id received and the
    ##        local ID. At last, send back the status.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __create_server(self, msg):

        ## New server data -- server label, imagem label and flavor type. The 
        ## network name is fixed (TODO).
        flvL = message['data']['flavor'];
        imgL = message['data']['image' ];
        vmsL = message['data']['name'  ];
        netL = NET_NAME;

        valret = self.__cloud.create_instance(vmsL, imgL, flvL, netL);

        status = valret[0];
        destId = valret[1];        

        if status == 'ACTIVE':

            ## Insert in the MAP table the origin uuid (player source) and the
            ## local instance uuid.
            self.__set_map_inst_id(destId, message['reqId']);

        return status;


    ##
    ## BRIEF: delete localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __delete_server(self, message):

        ## Obtain the local ID from MAP table.
        destId = self.__get_map_inst_id(message['reqId']);

        ## Delete the server:
        valret = self.__cloud.delete_instance(destId);

        status = valret[0];

        if status == 'HARD_DELETED':
            self.__get_map_inst_id(message['reqId'], True);

        return status;


    ##
    ## BRIEF: suspnd localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __suspnd_server(self, message):
        destId = self.__get_map_inst_id(message['data']['reqId']);

        ##status =self.__cloud.suspend_instance(instId);
        return 'NOT_IMPLEMENTED';


    ##
    ## BRIEF: resume localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __resume_server(self, message):
        destId = self.__get_map_inst_id(message['data']['reqId']);

        ## status =self.__cloud.resume_instance(instId);
        return 'NOT_IMPLEMENTED';


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

        ## Insert the message received into the database.
        mapping = Map();

        mapping.type_obj = 'instance';
        mapping.uuid_src = str(origId);
        mapping.uuid_dst = str(destId);
        mapping.date     = str(timeStamp);

        valRet = self.__db.insert_reg(mapping);

        return 0;


    ##
    ## Brief: get the local uuid from object.
    ## ------------------------------------------------------------------------
    ## @PARAM str  origId == origin uuid.
    ## @PARAM bool delete == check if is to delete entry.
    ##
    def __get_map_inst_id(self, origId, delete=False):
        destId = '';

        filterRules = {
            0 : Map.uuid_src == origId
        };

        ## Check if is possible create the new server (vcpu, memory, and disk).
        dReceived = self.__db.first_reg_filter(Map, filterRules);

        if dataReceived != []:
            destId = dataReceived[0]['destId'];

            if delete:

                filterRules = {
                    0 : Map.uuid_src == origId
                };

                valRet = self.__db.delete_reg(Map, filterRules);

        return destId;
## END.







###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    ## Get all configs parameters presents in the config file localized in CON-
    ## FIG_FILE path.
    config = get_configs(CONFIG_FILE);

    try:
        ## Authentication:
        mct_registry = MCT_Registry(config['main']);

        ## Register the player in the multicloud tournament:
        authStatus, authToken = mct_registry.registry();

        mct = MCT_Agent(config, authToken);
        mct.consume();

    except KeyboardInterrupt:
        pass;

    sys.exit(0);
## EOF
