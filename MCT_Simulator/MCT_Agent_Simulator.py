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
import os;

from mct.lib.utils               import *;
from mct.lib.emulator            import MCT_Emulator;
from mct.lib.amqp                import RabbitMQ_Publish, RabbitMQ_Consume;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy,Player,Request;
from mct.lib.registry            import MCT_Registry;
from mct.lib.security            import MCT_Security;
from mct.lib.sanity              import MCT_Sanity;
from mct.lib.instances           import MCT_Instances;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE           = 'mct-simulation.ini';
HOME_FOLDER           = os.path.join(os.environ['HOME'], CONFIG_FILE);
RUNNING_FOLDER        = os.path.join('./'              , CONFIG_FILE);
DEFAULT_CONFIG_FOLDER = os.path.join('/etc/mct/'       , CONFIG_FILE);









###############################################################################
## LOG                                                                       ##
###############################################################################
logging.basicConfig()








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
    __security     = None;
    __sanity       = None;
    __instances    = None;
    __dispatchId   = None;


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

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## Obtain some infomation that will necessary to correct running. The-
        ## re are: local address, external route to dispach, and dispatch id.
        self.__my_ip      = cfg['main']['my_ip'];
        self.__dispatchId = cfg['main']['dispatch_id'];
        self.__routeExt   = cfg['amqp_external_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, cfg['amqp_consume']);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publishExt = RabbitMQ_Publish(cfg['amqp_external_publish']);

        ## Instance a new object to handler all operation in the local databa-
        ## se (use SQLAlchemy).
        self.__db = MCT_Database_SQLAlchemy(cfg['database']);

        ## Instance a new object to handler all operation that cover envirome-
        ## nt sanity.
        self.__sanity = MCT_Sanity('player');
         
        ## Instance a new object to handler all operation that cover instance
        ## running in environment.
        self.__instances = MCT_Instances();

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

        ## LOG:
        self.__print.show("MESSAGE RECEIVED: " + str(message),'I');

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        ## Convert the json format to a structure than can handle by the python
        message = json.loads(message);

        ## Check if is a request received from players or a return from MCT.The
        ## identifier is the properties.app_id.
        if properties.app_id == self.__dispatchId:
             if self.__sanity.inspect_request(message) == True:
                 self.__recv_message_dispatch(message, properties.app_id);
        else:
             if self.__sanity.inspect_request(message) == True:
                 self.__send_message_dispatch(message, properties.app_id);

        return 0;


    ##
    ## BRIEF: consume stop.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        self.chn.basic_cancel(self.consumeTag);
        self.chn.close();
        self.connection.close();

        ## LOG:
        self.__print.show("\n###### STOP MCT_AGENT_SIMULATION ######\n",'I');
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
        self.__print.show('MESSAGE RECEIVED FROM AGENT...: '+str(message),'I');

        ## Insert the requet in object that mantain the VM running controller.
        if message['code'] == CREATE_INSTANCE:
            self.__instances.add_inst(message);

        ## Publish the message to dispatch (locate in remote server) via AMQP.
        valRet = self.__publishExt.publish(message, self.__routeExt);

        ## LOG:
        self.__print.show('MSG SENT '+str(message)+' ACKRET '+str(valRet),'I');

        return 0;


    ##
    ## BRIEF: receive message from MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ## @PARAM str  appId   == id from sender.
    ##
    def __recv_message_dispatch(self, message, appId):

        ## LOG:
        self.__print.show('MESSAGE RECEIVED FROM DISPATCH: '+str(message),'I');

        ## In this case,the MCT_Agent received actions from MCT to be performed
        ## locally. Execute and return to MCT dispatch.
        if message['destAddr'] != '':

            ## LOG:
            self.__print.show('PROCESSING REQUEST!', 'I');

            ## Select the appropriate action (create instance, delete instance,
            ## suspend instance e resume instance): 
            if   message['code'] == CREATE_INSTANCE:
                message = self.__create_server(message);

            elif message['code'] == DELETE_INSTANCE:
                message = self.__delete_server(message);

            ## LOG:
            self.__print.show('RETURN EXECUTION VALUE TO MCT DISPATCH!', 'I');

            ## Return data to MCT_Dispatch.
            self.__publishExt.publish(message, self.__routeExt);

        ## The second case, the message received from MCT Dispatch has the resu
        ## lt of action performed in other player.
        else:

            ## Check the return, if the action is to insert and return was suc-
            ## cefull: store the new vm instance in a special dictionary.
            if   message['code'] == CREATE_INSTANCE:
                self.__instances.upd_inst(message);

                ## LOG:
                self.__print.show("VMs Running: " +self.__instances.show(),'I');

            elif message['code'] == DELETE_INSTANCE:
                self.__instances.del_inst(message);

                ## LOG:
                self.__print.show("VMs Running: " +self.__instances.show(),'I');

            ## Update the database:
            self.__update_database(message);

        return 0;


    ##
    ## BRIEF: updata database with return value.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __update_database(self, message):

        ## Insert the message received into the database.
        request = Request();

        request.player_id  = str(message['playerId']);
        request.request_id = str(message['reqId'   ]);
        request.action     = int(message['code'    ]);
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
        dRecv=self.__db.all_regs_filter(Player,Player.name == msg['destName']);

        if dRecv != []:

            ## Max number of instances that the player can accept to be running.
            newInst = int(dRecv[-1]['running'      ]) + 1;
            maxInst = int(dRecv[-1]['max_instance' ]);
 
            if newInst <= maxInst:
                ## Check if exist the enough resources to alocate neu instance.
                if self.__check_resources(dRecv[-1], msg) == True:
                    status = 'ACTIVE';
            
        ## LOG:
        self.__print.show('>> STATUS ['+ status + '] FROM REQ '+str(msg), 'I');

        ## The MCT_Agent support more than one cloud framework. So is necessary
        ## prepare the return status to a generic format. Send back to dispatch
        ## the return for the request.
        msg['status'] = GENERIC_STATUS[msg['code']][status]; 

        return msg;


    ##
    ## BRIEF:  Check if exist the enough resources to alocate neu instance.
    ## ------------------------------------------------------------------------
    ## @PARAM playerInf == information about the player;
    ## @PARAM msg       == msg received.
    ##
    def __check_resources(self, playerInf, msg):

        ## Obtain the index that enable to get the flavor:
        flavor=FLV_NAME.keys()[FLV_NAME.values().index(msg['data']['flavor'])];

        nVcpuUsed = int(playerInf['vcpus_used'   ]) + int(CPU_INFO[flavor]);
        nMemoUsed = int(playerInf['memory_used'  ]) + int(MEM_INFO[flavor]);
        nDiskUsed = int(playerInf['local_gb_used']) + int(DSK_INFO[flavor]);
        nInstUsed = int(playerInf['running'      ]) + 1;

        ## Check if there are 'avaliable' resources to accept the instance.
        if  nVcpuUsed <= int(playerInf['vcpus'   ]) and \
            nMemoUsed <= int(playerInf['memory'  ]) and \
            nDiskUsed <= int(playerInf['local_gb']):

            ## Update the specific entry in dbase with new resource values.
            fieldsToUpdate = {
                'vcpus_used'   : nVcpuUsed,
                'memory_used'  : nMemoUsed,
                'local_gb_used': nDiskUsed,
                'running'      : nInstUsed
            };

            valRet=self.__db.update_reg(Player,
                                        Player.name ==  msg['destName'],
                                        fieldsToUpdate);
            return True;
        
        return False;


    ##
    ## BRIEF: delete localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __delete_server(self, msg):

        dRecv=self.__db.all_regs_filter(Player,Player.name == msg['destName']);

        if dRecv != []:

            ## Get the index that meaning the flavors.(vcpus, memory, and disk).
            flavor = self.__instances.flavor(msg);

            nVcpuUsed = int(dRecv[0]['vcpus_used'   ]) - int(CPU_INFO[flavor]);
            nMemoUsed = int(dRecv[0]['memory_used'  ]) - int(MEM_INFO[flavor]);
            nDiskUsed = int(dRecv[0]['local_gb_used']) - int(DSK_INFO[flavor]);
            nInstUsed = int(dRecv[0]['running'      ]) - 1;

            ## Update the specific entry in database with new resource values.
            fieldsToUpdate = {
                'vcpus_used'   : nVcpuUsed,
                'memory_used'  : nMemoUsed,  
                'local_gb_used': nDiskUsed,
                'running'      : nInstUsed
            };

            valRet=self.__db.update_reg(Player, Player.name == msg['destName'],
                                        fieldsToUpdate);

            msg['data']['vcpus'] = int(CPU_INFO[flavor]);
            msg['data']['mem'  ] = int(MEM_INFO[flavor]);
            msg['data']['disk' ] = int(DSK_INFO[flavor]);
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

## END CLASS.








class Main:

    """
    Class Main: main class.
    --------------------------------------------------------------------------
    PUBLIC METHODS:
    ** start == start the process.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __cfg     = None;
    __logger  = None;
    __print   = None;
    __running = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ##
    def __init__(self):

        ## Get the configurantion parameters.
        self.__cfg    = self.__get_configs();

        ## Configurate the logger. Use the parameters defineds in configuration
        ## file.
        self.__logger = self.__logger_setting(self.__cfg['log_agent']);


    ###########################################################################
    ## PUBLIC                                                                ##
    ###########################################################################
    ##
    ## BRIEF: start the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def start(self):
        self.__running = MCT_Agent(self.__cfg, self.__logger);
        self.__running.consume();
        return 0;


    ##
    ## BRIEF: stiop the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        self.__running.stop();
        return 0;


    ###########################################################################
    ## PRIVATE                                                               ##
    ###########################################################################
    ##
    ## BRIEF: get configuration from config file.
    ## ------------------------------------------------------------------------
    ##
    def __get_configs(self):
        cfgFileFound = '';

        ## Lookin in three places:
        ## 1 - user home.
        ## 2 - running folder.
        ## 3 - /etc/mct/
        for cfgFile in [HOME_FOLDER, RUNNING_FOLDER, DEFAULT_CONFIG_FOLDER]:
            if os.path.isfile(cfgFile):
                cfgFileFound = cfgFile;
                break;

        if cfgFileFound == '':
            raise ValueError('CONFIGURATION FILE NOT FOUND IN THE SYSTEM!');

        return get_configs(cfgFileFound);


    ## 
    ## BRIEF: setting logger parameters.
    ## ------------------------------------------------------------------------
    ## @PARAM settings == logger configurations.
    ##
    def __logger_setting(self, settings):

        ## Create a handler and define the output filename and the max size and
        ## max number of the files (1 mega = 1048576 bytes).
        handler = logging.handlers.RotatingFileHandler(
                                  filename    = settings['log_filename'],
                                  maxBytes    = int(settings['file_max_byte']),
                                  backupCount = int(settings['backup_count']));

        ## Create a foramatter that specific the format of log and insert it in
        ## the log handler. 
        formatter = logging.Formatter(settings['log_format']);
        handler.setFormatter(formatter);

        ## Set up a specific logger with our desired output level (in this case
        ## DEBUG). Before, insert the handler in the logger object.
        logger = logging.getLogger(settings['log_name']);
        logger.setLevel(logging.DEBUG);
        logger.addHandler(handler);

        return logger;

## END.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    try:
        main = Main();
        main.start();

    except ValueError as exceptionNotice:
        print exceptionNotice;

    except KeyboardInterrupt:
        main.stop();
        print "BYE!";

    sys.exit(0);
## EOF
