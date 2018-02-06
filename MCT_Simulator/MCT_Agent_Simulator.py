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
#logging.basicConfig()








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
    __routeInt        = None;
    __routeExt        = None;
    __publishInt      = None;
    __publishExt      = None;
    __my_ip           = None;
    __cloud           = None;
    __cloudType       = None;
    __db              = None;
    __print           = None;
    __security        = None;
    __sanity          = None;
    __instances       = None;
    __dispatchId      = None;
    __debug           = None;
    __vplayerStrategy = {};
    __vplayerCoalition= {};


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
        self.__debug      = cfg['main']['debug'];  

        ## Publish configuration.
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
        self.__print.show("\n###### START MCT_AGENT_SIMULATION ######", 'I');


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: method invoked when the pika receive a message.
    ## ------------------------------------------------------------------------
    ## @PARAM pika.Channel              channel    = the communication channel.
    ## @PARAM pika.spec.Basic.Deliver   method     = 
    ## @PARAM pika.spec.BasicProperties properties = 
    ## @PARAM str                       msg        = message received.
    ##
    def callback(self, channel, method, properties, msg):
        idv = properties.app_id; 

        ## LOG:
        self.__print.show("MESSAGE RECEIVED FROM "+str(idv)+" -"+str(msg),'I');

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        ## Convert the json format to a structure than can handle by the python
        msg = json.loads(msg);

        ## Check if is a request received from players or a return from MCT.The
        ## identifier is the properties.app_id.
        if idv == self.__dispatchId:
             if self.__sanity.inspect_request(msg) == True:
                 self.__recv_message_dispatch(msg, idv);
        else:
             if self.__sanity.inspect_request(msg) == True:
                 self.__send_message_dispatch(msg, idv);

        ## LOG:
        self.__print.show('------------------------------------------\n', 'I');
        return SUCCESS;


    ##
    ## BRIEF: consume stop.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):

        self.chn.basic_cancel(self.consumeTag);
        self.chn.close();
        self.connection.close();

        ## LOG:
        self.__print.show("###### STOP MCT_AGENT_SIMULATION ######\n",'I');
        return SUCCESS;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: send message to MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg   == received message.
    ## @PARAM str  appId == id from sender.
    ##
    def __send_message_dispatch(self, msg, appId):

        ## Insert the requet in object that mantain the VM running controller.
        if   msg['code'] == CREATE_INSTANCE:
             if self.__prepare_msg_to_go_add(msg) == FAILED:
                 return FAILED; 

        ## Insert the requet in object that mantain the VM running controller.
        elif msg['code'] == DELETE_INSTANCE:
             if self.__prepare_msg_to_go_del(msg) == FAILED:
                 return FAILED; 

        elif msg['code'] == SETINF_RESOURCE:
            ## Before send the messagem to dispatch update local vplayer data-
            ## base.
            self.__set_localy_info_resources(msg);

        ## Publish the message to dispatch (locate in remote server) via AMQP.
        valRet = self.__publishExt.publish(msg, self.__routeExt);
        return SUCCESS;


    ##
    ## BRIEF: check if exist other vm with the same ID.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __prepare_msg_to_go_add(self, msg):
        data = {
            'data' : {
                'origNm' : str(msg['playerId']),
                'origId' : str(msg['reqId'   ])
            }
        };

        ## Check if the instance to delete is running: 
        if self.__instances.is_alive(data) == SUCCESS:
            ## LOG:
            self.__print.show('INSTANCE DUPLICATED: ' + str(msg), 'I');

            msg['status'] = ERROR_DB_ADD;

            ## Update the database:
            self.__update_database(msg);
            return FAILED;

        self.__instances.add_instance(msg);
        return SUCCESS;


    ##
    ## BRIEF: check if exist with the same ID.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __prepare_msg_to_go_del(self, msg):
        data = {
            'data' : {
                'origNm' : str(msg['playerId']),
                'origId' : str(msg['reqId'   ])
            }
        };

        ## Check if the instance to delete is running: 
        if self.__instances.is_alive(data) == FAILED:
            ## LOG:
            self.__print.show('INSTANCE NOT FOUND: ' + str(msg), 'I');

            msg['status'] = ERROR_DB_DEL;

            ## Update the database:
            self.__update_database(msg);
            return FAILED;

        return SUCCESS;


    ##
    ## BRIEF: receive message from MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg   == received message.
    ## @PARAM str  appId == id from sender.
    ##
    def __recv_message_dispatch(self, msg, appId):

        ## In this case,the MCT_Agent received actions from MCT to be performed
        ## locally. Execute and return to MCT dispatch.
        if msg['destAddr'] != '':
            self.__remote(msg);

        ## The second case, the message received from MCT Dispatch has the resu
        ## lt of action performed in other player.
        else:
            self.__localy(msg);

        return SUCCESS;


    ##
    ## BRIEF: execute actions "remote" (actions received from DISPATCH).
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __remote(self, msg):
        ## LOG:
        self.__print.show('REMOTE EXECUTION!', 'I');

        ## Select the appropriate action (create instance, delete server, sus-
        ## pend instance e resume instance): 
        if   msg['code'] == CREATE_INSTANCE:
            msg = self.__create_server(msg);

        elif msg['code'] == DELETE_INSTANCE:
            msg = self.__delete_server(msg);

        elif msg['code'] == SANITY_INSTANCE:
            msg = self.__sanity_server(msg);

        ## LOG:
        self.__print.show('RET. EXEC VALUE TO MCT DISPATCH: ' + str(msg), 'I');

        ## Return data to MCT_Dispatch.
        self.__publishExt.publish(msg, self.__routeExt);

        return SUCCESS;

 
    ##
    ## BRIEF: execute actions "localy" (return - result from action).
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __localy(self, msg):

        ## LOG:
        self.__print.show('RETURN FROM ACTION!', 'I');

        ## Remove player from table:
        if msg['status'] == PLAYER_REMOVED:
            self.__remove_player_from_simulation(msg);

        ## Handle the action return:
        ############################
        if   msg['code'] == CREATE_INSTANCE:
            ## Define vplayer behavior. If diff of AWARE the player is using the 
            ## cheating and will be destroy the VM after accept the request.
            try:
                strategy = self.__vplayerStrategy[msg['destName']];
            except:
                pass;

            if   msg['status'] == SUCCESS and strategy == COALITION:
                self.__instances.upd_instance(msg);

            elif msg['status'] == SUCCESS and strategy == AWARE:
                self.__instances.upd_instance(msg);

            else:
                self.__instances.del_instance(msg);

        ## DEL LOCALY INSTANCE - RETURN OF REQUEST:
        elif msg['code'] == DELETE_INSTANCE:
            if msg['status'] == SUCCESS or msg['status'] == PLAYER_REMOVED:
                self.__instances.del_instance(msg);
            
        ## ADD LOCALY INSTANCE - RETURN OF REQUEST:
        elif msg['code'] == ADD_REG_PLAYER:
            if msg['status'] == SUCCESS:
                self.__return_of_register_player(msg);

        ## GET PLAYER INFORMA. - RETURN OF REQUEST:
        elif msg['code'] == GETINF_RESOURCE:
            if msg['status'] == SUCCESS:
                self.__return_of_get_inf_resources(msg);

        ## Update the database:
        self.__update_database(msg);

        ## Get and show from 'MCT_Instance' object status of all instances.
        self.__show_all_instances_status();

        return SUCCESS;


    ##
    ## BRIEF: remove player from database.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __remove_player_from_simulation(self, msg):

        ## LOG:
        self.__print.show('DISABLE PLAYER: ' + str(msg), 'I');

        data = {
           'enabled' : PLAYER_DISABLED
        };

        self.__db.update_reg(Player, Player.name == msg['playerId'],  data);
        return SUCCESS;


    ##
    ## BRIEF: return of request -- get info resources.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __return_of_get_inf_resources(self, msg):

        ## Insert the player in database:
        data = {
            'fairness': msg['data']['fairness']
        };
     
        self.__db.update_reg(Player, Player.name == msg['playerId'],  data);

        ## LOG:
        self.__print.show('VPLAYER ' + msg['playerId']+' SET FAIRNESS', 'I');

        return SUCCESS;


    ##
    ## BRIEF: return of request "register player' - set token in database.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __return_of_register_player(self, msg):
        status = FAILED;

        try:
            ## Insert the player in database:
            player = Player();

            player.name     = msg['playerId'];
            player.address  = msg['origAddr'];
            player.division = 0;
            player.token    = msg['data']['token'];

            valRet = self.__db.insert_reg(player);
            status = SUCCESS;

            ## LOG:
            self.__print.show('VPLAYER '+msg['playerId']+' INSERTED IN MCT','I');

        except:
            ## LOG:
            self.__print.show('VPLAYER '+msg['playerId']+' YET INSERTED', 'I');

        return status;


    ##
    ## BRIEF: before send the messagem to dispatch update local vplayer db.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __set_localy_info_resources(self, msg):

        data = {
           'vcpus'        : msg['data']['vcpus'       ],
           'memory'       : msg['data']['memory'      ],
           'local_gb'     : msg['data']['local_gb'    ],
           'max_instance' : msg['data']['max_instance'],
        };

        self.__db.update_reg(Player, Player.name == msg['playerId'], data);

        ## Set virtual player strategy:
        self.__vplayerStrategy[msg['playerId']] = msg['data']['strategy'];  

        ## If the vplayer pefil is coalition, set virtual player coalition mem-
        ## bers.
        if msg['data']['strategy'] == COALITION:
            self.__vplayerCoalition[msg['playerId']] =msg['data']['coalition'];

        return SUCCESS;


    ##
    ## BRIEF: updata database with return value.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __update_database(self, msg):

        ## Insert the message received into the database.
        request = Request();

        request.player_id  = str(msg['playerId']);
        request.request_id = str(msg['reqId'   ]);
        request.action     = int(msg['code'    ]);
        request.status     = int(msg['status'  ]);
        request.message    = str(msg['data'    ]);

        valRet = self.__db.insert_reg(request);
        return SUCCESS;


    ##
    ## BRIEF: create localy a new server. 
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __create_server(self, msg):
        status = FAILED;

        ## Check if is possible create the new server (vcpu, memory, and disk).
        dRecv=self.__db.all_regs_filter(Player,Player.name == msg['destName']);

        idx = msg['destName'] + '_' + str(self.__create_index());                  

        if dRecv != []:
            strategy = self.__vplayerStrategy[msg['destName']];

            ##
            ## Player is a tipical Free-Rders, denny all request by instances.
            ##
            if   strategy == FREERIDER:
                pass;

            ##
            ## Player is in cheating mode, accept but not execute the instance.
            ##
            elif strategy == CHEATING :
                 msg['retId']=idx; 
                 status = SUCCESS;

            ##
            ## Player is in coalition mode, accept but not execute the instance.
            ##
            elif strategy == COALITION:
                 ## Check if the player requested is member of coalition,if yes
                 ## accept the request, otherwise reject.
                 if msg['playerId'] in self.__vplayerCoalition[msg['destName']]:
                     msg['retId']=idx; 
                     status = SUCCESS;

            ##
            ## Enviroment aware:
            ##
            else:
                ## Max number of instances that the player can accept to be run
                ## ning.
                newInst = int(dRecv[-1]['running'     ]) + 1;
                maxInst = int(dRecv[-1]['max_instance']);
 
                if (newInst <= maxInst):
                    ## Check if exist the enough resources to alocate new "VM".
                    if self.__check_resources(dRecv[-1], msg) == SUCCESS:
                        msg['retId']=idx; 
                        status = SUCCESS;
        
        ## LOG:
        self.__print.show('>> STATUS ['+str(status)+'] FROM REQ '+str(msg),'I');

        msg['status'] = status;
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
        f0 = int(playerInf['vcpus'   ]);
        f1 = int(playerInf['memory'  ]);
        f2 = int(playerInf['local_gb']);

        if  nVcpuUsed <= f0 and nMemoUsed <= f1 and nDiskUsed <= f2:

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
            return SUCCESS;
        
        return FAILED;


    ##
    ## BRIEF: delete localy a new server.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __delete_server(self, msg):

        dRecv=self.__db.all_regs_filter(Player,Player.name == msg['destName']);

        if dRecv != []:
            ## Get the index that meaning the flavors.(vcpus, memory, and disk).
            flavor = self.__instances.get_flavor(msg);

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


    ##
    ## BRIEF: check if an instance is running.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == received message.
    ##
    def __sanity_server(self, msg):

        ## LOG:
        self.__print.show('>> [FROM MCT_SANITY] CHECK INSTANCE: '+str(msg),'I');

        ## Check if instance is running:
        ## ------------------------------
        ## origNm == the name of running instance player.
        ## origId == instance id (generate in the player origin).
        ##
        msg['status'] = self.__instances.is_alive(msg);

        ## LOG:
        self.__print.show('>> RETURN FROM SANITY: '+str(msg),'I');
        return msg;


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
    ## BRIEF: Get and show from 'MCT_Instance' object status of all instances.
    ## ------------------------------------------------------------------------
    ##
    def __show_all_instances_status(self):

        ## Get and show all instances in enviromment:
        allInsts = self.__instances.show();
      
        for player in allInsts:

            ## LOG:
            self.__print.show(player, 'I');

            for iid in allInsts[player]:
                ## LOG:
                self.__print.show('>> '+str(iid)+' '+str(allInsts[player][iid]),'I');

        return SUCCESS;

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
