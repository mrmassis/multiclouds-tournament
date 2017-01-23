#!/usr/bin/env python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
import sys;
import json;
import time;
import logging;
import logging.handlers;
import pika;
import datetime;
import hashlib;

from mct.lib.utils               import *;
from mct.lib.emulator            import MCT_Emulator;
from mct.lib.amqp                import RabbitMQ_Publish, RabbitMQ_Consume;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy,Player,Request;
from mct.lib.registry            import MCT_Registry;








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
    Class MCT_Agent - agent modified to be used in simulation. 
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    ** callback == method invoked when the pika receive a message.

    PRIVATE METHODS:    
    ** __recv_message_referee == receive message from referee.
    ** __send_message_referee == send message to referee.
    ** __inspect_request      == check if all necessary fields are in request.
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
    __print        = None;
    __insts        = {};


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM dict cfg    == dictionary with configurations about MCT_Agent.
    ## @PARAM obj  logger == logger object.
    ##
    def __init__(self, cfg, authToken):

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## Local address:
        self.__my_ip = cfg['main']['my_ip'];

        ## Get which route is used to deliver the msg to the 'correct destine'.
        self.__routeExt = cfg['amqp_external_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, config['amqp_consume']);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publishExt = RabbitMQ_Publish(cfg['amqp_external_publish']);

        ## Intance a new object to handler all operation in the local database.
        self.__db = MCT_Database_SQLAlchemy(cfg['database']);

        ## Setting the player's authentication token:
        self.__authToken = authToken;

        ## LOG:
        self.__print.show("\n###### START MCT_AGENT_SIMULATION ######\n",'I');


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
    ## @PARAM str  appId   == id from sender.
    ##
    def __send_message_dispatch(self, message, appId):

        ## LOG:
        self.__print.show('MESSAGE TO DISPATCH ' + str(message), 'I');

        ##
        ## TODO: put in a specific module!!!
        ## Verify if the vPlayer has authorization to send mssg to MCT_Referee.
        valRet = self.__check_vplayer_access(message['playerId']);

        ## Publish the message to MCT_Dispatch via AMQP. The MCT_Dispatch is in
        ## the remote server. 
        valRet = self.__publishExt.publish(message, self.__routeExt);

        if valRet == False:
            ## LOG:
            self.__print.show('IT WAS NOT POSSIBLE TO SEND THE MESSAGE!', 'E');
        else:
            ## LOG:
            self.__print.show('MESSAGE SENT TO DISPATCH!', 'I');
      
        return 0;


    ##
    ## BRIEF: receive message from MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ## @PARAM str  appId   == id from sender.
    ##
    def __recv_message_dispatch(self, message, appId):

        ## LOG:
        self.__print.show('MESSAGE RETURNED FROM REFEREE: '+str(message), 'I');

        ## In this case, the MCT_Agent received actions to be performed locally.
        if message['destAddr'] != '':

            ## LOG:
            self.__print.show('PROCESSING REQUEST!', 'I');

            ## Select the appropriate action (create instance, delete instance,
            ## suspend instance e resume instance): 
            ## Create:
            if   message['code'] == CREATE_INSTANCE:
                message = self.__create_server(message);

            ## Delete:
            elif message['code'] == DELETE_INSTANCE:
                message = self.__delete_server(message);

            ## LOG:
            self.__print.show('RETURN TO DISPATCH!', 'I');

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
        request = Request();

        request.player_id  = str(message['playerId']);
        request.request_id = str(message['reqId'   ]);
        request.status     = int(message['status'  ]);
        request.message    = str(message['data'    ]);

        valRet = self.__db.insert_reg(request);


    ##
    ## BRIEF: create localy a new server. 
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __create_server(self, msg):

        status = 'ERROR';

        ## Check if is possible create the new server (vcpu, memory, and disk).
        dReceived=self.__db.first_reg_filter(Player, 
                                          Player.player_id == msg['destName']);

        if dReceived != []:

            ## Get the index that meaning the flavors.(vcpus, memory, and disk).
            i =FLV_NAME.keys()[FLV_NAME.values().index(msg['data']['flavor'])];

            newVcpuUsed = int(dReceived[0]['vcpus_used'    ])+int(CPU_INFO[i]);
            newMemoUsed = int(dReceived[0]['memory_mb_used'])+int(MEM_INFO[i]);
            newDiskUsed = int(dReceived[0]['local_gb_used' ])+int(DSK_INFO[i]);

            ## Check if there are 'avaliable' resources to accept the instance.
            if  newVcpuUsed <= dReceived[0]['vcpus'   ] and \
                newMemoUsed <= dReceived[0]['memory'  ] and \
                newDiskUsed <= dReceived[0]['local_gb']:

                ## Update the specific entry in dbase with new resource values.
                fieldsToUpdate = {
                    'vcpus_used'     : newVcpuUsed,
                    'memory_mb_used' : newMemoUsed,  
                    'local_gb_used'  : newDiskUsed
                };

                valRet=self.__db.update_reg(Player, 
                                            Player.player_id == msg['destName'],
                                            fieldsToUpdate);

                ## Store the new virtual machine instance in a special structu-
                ## re. A dictionary:
                self.__insert_instance_to_dictionary(msg);

                status = 'ACTIVE';

        ## LOG:
        self.__print.show('>> STATUS '+str(status)+' FROM REQ '+str(msg), 'I');

        ## The MCT_Agent support more than one cloud framework. So is necessary
        ## prepare the return status to a generic format. Send back to dispatch
        ## the return for the request.
        msg['status'] = GENERIC_STATUS[msg['code']][status]; 

        return msg;


    ##
    ## BRIEF: delete localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __delete_server(self, msg):

        dReceived=self.__db.first_reg_filter(Player, 
                                          Player.player_id == msg['destName']);

        if dReceived != []:

            ## Remove a virtual machine instance in a special structure. A dic-
            ## tionary:
            flavorId = self.__remove_instance_from_dictionary(msg);

            ## Get the index that meaning the flavors.(vcpus, memory, and disk).
            i = FLV_NAME.keys()[FLV_NAME.values().index(flavorId)];

            newVcpuUsed = int(dReceived[0]['vcpus_used'    ])-int(CPU_INFO[i]);
            newMemoUsed = int(dReceived[0]['memory_mb_used'])-int(MEM_INFO[i]);
            newDiskUsed = int(dReceived[0]['local_gb_used' ])-int(DSK_INFO[i]);

            ## Update the specific entry in database with new resource values.
            fieldsToUpdate = {
                'vcpus_used'     : newVcpuUsed,
                'memory_mb_used' : newMemoUsed,  
                'local_gb_used'  : newDiskUsed
            };

            valRet=self.__db.update_reg(Player, 
                                        Player.player_id == msg['dstName'],
                                        fieldsToUpdate);

            msg['data']['vcpus'] = int(CPU_INFO[i]);
            msg['data']['mem'  ] = int(MEN_INFO[i]);
            msg['data']['disk' ] = int(DSK_INFO[i]);

        else:

            msg['data']['vcpus'] = 0;
            msg['data']['mem'  ] = 0;
            msg['data']['disk' ] = 0;

        ## LOG:
        self.__print.show('>> STATUS HARD DELETED FROM REQ ' + str(msg), 'I');

        ## The MCT_Agent support more than one cloud framework. So is necessary
        ## prepare the return status to a generic format. Send back to dispatch
        ## the return for the request.
        msg['status'] = GENERIC_STATUS[msg['code']]['HARD_DELETED']; 

        return msg;


    ##
    ## BRIEF: check if all necessary fields are in the request.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __inspect_request(self, request):
        return 0;


    ##
    ## BRIEF: insert an instance in structure.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def __insert_instance_to_dictionary(self, msg):

        if not msg['destName'] in self.__insts:
          self.__insts[msg['destName']] = {}

        ##  Insert the instance in dictionary:
        self.__insts[msg['destName']][msg['reqId']] = msg['data']['flavor'];

        ## LOG:
        self.__print.show('-- INSTANCES: ' + str(self.__insts), 'I');
        


    ##
    ## BRIEF: remove an instance from structure.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def __remove_instance_from_dictionary(self, message):

        ## Remove the instance entry from dictionary and return the flavorID.
        flavorId = self.__insts[msg['destName']].pop([msg['reqId']], None);

        ## LOG:
        self.__print.show('[INSTANCES RUNNING] - ' + str(self.__insts), 'I');

        return flavorId;


    ##
    ## TODO: put in the specific module!
    ## BRIEF: verify if vPlayer has authorization to send msg to MCT_Referee.
    ## ------------------------------------------------------------------------
    ## @PARAM playerId == player identification
    ##
    def __check_vplayer_access(self, playerId):
        return 0;

## END.







###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    config = get_configs(CONFIG_FILE);

    try:
        ##
        tokens = [];

        ## Case this agent is virtual (to emulate), open the file with vagents
        ## specification.
        for i in range(int(config['main']['vplayers'])):
            vName = 'vplayer' + str(i);

            ## Get configuration options to the virtual player (amqp,quote etc)
            vCfg = config[vName];
    
            try:
                mct_registry = MCT_Registry(vCfg);

                ## Register the virtual player in the tournament. Return status
                ## and the authentication token.
                authStatus, authToken = mct_registry.registry();

                ## Store the token:
                tokens.append({'name'      : vName,
                               'authStatus': authStatus,
                               'authToken' : authToken}
                             );
            except:
                pass;

        mct = MCT_Agent(config, tokens);
        mct.consume();

    except KeyboardInterrupt:
        pass;

    sys.exit(0);
## EOF
