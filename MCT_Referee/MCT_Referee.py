#!/usr/bin/env python


import time;
import sys;
import os;
import datetime;
import json;
import logging;
import logging.handlers;

from sqlalchemy                  import and_, or_;
from multiprocessing             import Process, Queue, Lock;
from mct.lib.scheduller          import *;
from mct.lib.amqp                import RabbitMQ_Publish, RabbitMQ_Consume;
from mct.lib.utils               import *;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy, Player, Vm;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE           = 'mct-referee.ini';
HOME_FOLDER           = os.path.join(os.environ['HOME'], CONFIG_FILE);
RUNNING_FOLDER        = os.path.join('./'              , CONFIG_FILE);
DEFAULT_CONFIG_FOLDER = os.path.join('/etc/mct/'       , CONFIG_FILE);








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Referee(RabbitMQ_Consume):

    """
    Class MCT_Referee: start and mantain the MCT referee.
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    ** callback == waiting for requests.
    ** stop     == consume stop.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __threadsId     = None;
    __allQueues     = None;
    __routeDispatch = None;
    __db            = None;
    __scheduller    = None;
    __print         = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM cfg    == dictionary with configurations about MCT_Agent.
    ## @PARAM logger == logger object.
    ##
    def __init__(self, cfg, logger):

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## Get which route is used to deliver the message to the MCT_Dispatch.
        self.__routeDispatch = cfg['amqp_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, cfg['amqp_consume']);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish = RabbitMQ_Publish(cfg['amqp_publish']);

        ## Intance a new object to handler all operation in the local database
        self.__db = MCT_Database_SQLAlchemy(cfg['database']);

        ## Select the scheduller algorithm responsible for selection of the be-
        ## st player in a division.
        schedullerOption = cfg['scheduller']['approach'];

        ## Choice the scheduller:
        if schedullerOption == 'round_robin_imutable_list':
            self.__scheduller=Round_Robin_Imutable_List();
        else:
            pass;

        ## LOG:
        self.__print.show("###### START MCT_REFEREE ######\n",'I');


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
        appId = properties.app_id;

        ## LOG:
        self.__print.show('MESSAGE RECEIVED: ' + msg + ' Id: '+ appId,'I');

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        ## The json.loads translate a string containing JSON data into a Python
        ## dictionary format.
        msg = json.loads(msg);

        ## Get which division than player belong. It is necessary to get player
        ## list able to meet the request.
        division = self.__get_division(msg['playerId']);

        ## Check if division is invalid (-1) -- util.py:
        if division == DIVISION_INVALID:
            msg['retId' ] = '';
            msg['status'] = 0 ;

        ## ----------------------------------------------------------------- ##
        ## GET RESOUCES INF.                                                 ##
        ## ----------------------------------------------------------------- ##
        if   int(msg['code']) == GETINF_RESOURCE:
            ## LOG:
            self.__print.show('GETINF' ,'I');
            msg['data'] = self.__get_resources_inf(division);

        ## ----------------------------------------------------------------- ##
        ## SET RESOUCES INF.                                                 ##
        ## ----------------------------------------------------------------- ##
        elif int(msg['code']) == SETINF_RESOURCE:
            ## LOG:
            self.__print.show('SETINF' ,'I');
            msg['data'] = self.__set_resources_inf(division, msg);

        ## ----------------------------------------------------------------- ##
        ## CREATE A NEW INSTANCE.                                            ##
        ## ----------------------------------------------------------------- ##
        elif int(msg['code']) == CREATE_INSTANCE:
            ## LOG:
            self.__print.show('CREATE' ,'I');
            msg = self.__add_instance(division, msg);

        ## ----------------------------------------------------------------- ##
        ## DELETE AN INSTANCE.                                               ##
        ## ----------------------------------------------------------------- ##
        elif int(msg['code']) == DELETE_INSTANCE:
            ## LOG:
            self.__print.show('DELETE' ,'I');
            msg = self.__del_instance(division, msg);

        ## ----------------------------------------------------------------- ##
        ## GET INSTANCE INFO.                                                ##
        ## ----------------------------------------------------------------- ##
        elif int(msg['code']) == GETINF_INSTANCE:
            ## LOG:
            self.__print.show('VMINF' ,'I');
            msg = self._inf_instance(division, msg);

        self.__publish.publish(msg, self.__routeDispatch);

        ## LOG:
        self.__print.show('------------------------------------------\n', 'I');
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
        self.__print.show("###### STOP MCT_REFEREE ######\n",'I');
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: get the player's division.
    ## ------------------------------------------------------------------------
    ## @PARAM str player == player identifier.
    ##
    def __get_division(self, player):

        ## LOG:
        self.__print.show('GET PLAYER DIVISION!', 'I');

        ## Setting: 
        division = DIVISION_INVALID;

        ## Perform a select to get all vm instances assign (running) in 'vPlayer'.
        dRecv = self.__db.all_regs_filter(Player, (Player.name == player));

        if dRecv != []:
            division = dRecv[0]['division'];

        return division;


    ##
    ## BRIEF: get info instance.
    ## ------------------------------------------------------------------------
    ## @PARAM int division == division from player who request.
    ## @PARAM dict msg     == message data.
    ##
    def __inf_instance(self, division, msg):

        ## LOG:
        self.__print.show('GET INFORMATION ABOUT INSTANCE: ' + str(msg), 'I');

        ## SENDTO: If 'retId == empty' the request is go to the player destiny.
        if msg['retId'] == '':
            msg = self.__inf_instance_send_destiny(msg);

        ## RETURN: If retId !='' the request is return from the player destiny. 
        else:
            msg = self.__inf_instance_recv_destiny(msg);

        return msg;


    ##
    ## BRIEF: send get inf instance to destiny.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == message data.
    ## 
    def __inf_instance_send_destiny(self, msg):

        ## LOG:
        self.__print.show('INI GET INSTANCE INF SEND','I');

        ## Obtain the information about who is executing the virtual machine.
        dRecv = self.__db.all_regs_filter(Vm, (Vm.origin_id == msg['reqId']));

        if dRecv != []:
            destinyAdd = str(dRecv[-1]['destiny_add']);

            ## LOG:
            self.__print.show('GET INF FROM TO ADDR ' + destinyAdd, 'I');

            ## Set the message to be a forward message (perform a map). Send it
            ## to the destine and waiting the return.
            msg['retId'] = msg['reqId'];

            ## Set the target address. The target addr is the player addrs that
            ## will accept the request.
            msg['destAddr'] = dRecv[-1]['destiny_add' ];
            msg['destName'] = dRecv[-1]['destiny_name'];

            ## LOG:
            self.__print.show('GET INF SEND: PLAYER VALUES '+str(msg),'I');
        else:
            ## LOG:
            self.__print.show('THERE ISNT PLAYER EXECUTING THIS INST.!', 'I');
            msg['status'] = FAILED;

        ## LOG:
        self.__print.show('END GET INF SEND', 'I');
        return msg;


    ##
    ## BRIEF: recv get inf instance from destiny.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg == message data.
    ## 
    def __inf_instance_recv_destiny(self, msg):

        ## Set the destAddr and retId fields to give back response to player.
        msg['destAddr'] = '';
        msg['retId'   ] = '';

        ## LOG:
        self.__print.show('END GET INF RECV','I');
        return msg;


    ##
    ## ------------------------------------------------------------------------
    ## @PARAM int division == division from player who request.
    ## @PARAM dict msg     == message data.
    ##
    def __add_instance(self, division, msg):

        ## LOG:
        self.__print.show('CREATE INSTANCE: ' + str(msg['reqId']), 'I');

        ## SENDTO: If 'retId == empty' the request is go to the player destiny.
        if msg['retId'] == '':
            msg = self.__add_instance_send_destiny(division, msg);

        ## RETURN: If retId !='' the request is return from the player destiny. 
        else:
            msg = self.__add_instance_recv_destiny(division, msg);

        return msg;


    ##
    ## BRIEF: delete an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM int division == the player division .
    ## @PARAM dict message == message with some datas to delete an instance.
    ##
    def __del_instance(self, division, msg):

        ## LOG:
        self.__print.show('DELETE INSTANCE: '+str(msg), 'I');

        ## SENDTO: If 'retId == empty' the request is go to the player destiny.
        if msg['retId'] == '':
            msg = self.__del_instance_send_destiny(division, msg);

        ## RETURN: If retId !='' the request is return from the player destiny. 
        else:
            msg = self.__del_instance_recv_destiny(division, msg);

        return msg;


    ##
    ## BRIEF: send add message to destiny.
    ## ------------------------------------------------------------------------
    ## @PARAM int division == division from player who request.
    ## @PARAM dict msg     == message data.
    ##
    def __add_instance_send_destiny(self, division, msg):

        ## Select one player able to comply a request to create VM. Inside the-
        ## se method is selected the scheduller approach.
        selectedPlayer = self.__get_player(division, msg['playerId']);

        if selectedPlayer != {}:

            ## LOG:
            self.__print.show('SELECTED PLAYER: ' + str(selectedPlayer), 'I');

            ## Set the message to be a forward message (perform a map). Send it
            ## to the destine and waiting the return.
            msg['retId'] = msg['reqId'];

            ## Set the target address. The target addr is the player' addrs that
            ## will accept the request.
            msg['destName'] = selectedPlayer['name'   ];
            msg['destAddr'] = selectedPlayer['address'];

            ## LOG:
            self.__print.show('SEND REQ TO SELECTED DESTINY: '+ str(msg), 'I');
        else:
            ## LOG:
            self.__print.show('THERE ISNT PLAYER ABLE TO EXEC: '+str(msg),'E');

            ## Case not found a player to execute the request setting status to
            ## error and return the message to origin.
            msg['status'] = 0;

        return msg;


    ##
    ## BRIEF: receive add message from destiny. 
    ## ------------------------------------------------------------------------
    ## @PARAM int division == division from player who request.
    ## @PARAM dict msg     == message data.
    ##
    def __add_instance_recv_destiny(self, division, msg):

        ## LOG:
        self.__print.show('RETURN FROM ADD_INSTANCE IS: ' + str(msg),'I');

        vm = Vm();

        vm.origin_id          = msg['reqId'   ];
        vm.origin_add         = msg['origAddr'];
        vm.origin_name        = msg['playerId'];
        vm.destiny_name       = msg['destName'];
        vm.destiny_add        = msg['destAddr'];
        vm.destiny_id         = msg['retId'   ];
        vm.status             = msg['status'  ];
        vm.vcpus              = int(msg['data']['vcpus']);
        vm.mem                = int(msg['data']['mem'  ]);
        vm.disk               = int(msg['data']['disk' ]);
        vm.timestamp_received = str(datetime.datetime.now());

        ## Vm creation request failed.
        if msg['status'] != SUCCESS:
            vm.timestamp_finished = vm.timestamp_received;

        ## Insert in database.
        valRet = self.__db.insert_reg(vm);

        ## Update all values of used resources. The table used is the "PLAYER".
        ## the table has all resources offer and used by the player.:
        self.__update_used_values(CREATE_INSTANCE, msg);

        msg['destAddr'] = '';
        msg['retId'   ] = '';

        return msg;


    ##
    ## BRIEF: send del message to destiny.
    ## ------------------------------------------------------------------------
    ## @PARAM int division == division from player who request.
    ## @PARAM dict msg     == message data.
    ##
    def __del_instance_send_destiny(self, division, msg):

        ## LOG:
        self.__print.show('INI DEL SEND','I');

        ## Obtain the information about who is executing the virtual machine.
        dRecv = self.__db.all_regs_filter(Vm, (Vm.origin_id == msg['reqId']));

        if dRecv != []:
            ## LOG:
            self.__print.show('DEL TO ADDR '+str(dRecv[-1]['destiny_add']),'I');

            ## Set data:
            msg['retId'   ] = dRecv[-1]['destiny_id'  ];
            msg['destAddr'] = dRecv[-1]['destiny_add' ];
            msg['destName'] = dRecv[-1]['destiny_name'];

            ## LOG:
            self.__print.show('DEL SEND: PLAYER VALUES '+str(msg),'I');
        else:
            ## LOG:
            self.__print.show('THERE ISNT PLAYER EXECUTING THIS INST.!', 'I');
            msg['status'] = FAILED;

        ## LOG:
        self.__print.show('END DEL SEND','I');
        return msg;


    ##
    ## BRIEF: receive del message from destiny. 
    ## ------------------------------------------------------------------------
    ## @PARAM int division == division from player who request.
    ## @PARAM dict msg     == message data.
    ##
    def __del_instance_recv_destiny(self, division, msg):

        ## LOG:
        self.__print.show('INI DEL RECV','I');

        ## LOG:
        self.__print.show('RETURN FROM DEL_INST IS ' + str(msg['status']), 'I');

        if msg['status'] == SUCCESS:
            data = {
                'timestamp_finished' : str(datetime.datetime.now()),
                'status'             : FINISHED
            };
        else:
            data = {
                'timestamp_finished' : str(datetime.datetime.now()),
                'status'             : FAILED
            };

        self.__db.update_reg(Vm, Vm.origin_id == msg['reqId'], data);

        ## the table has all resources offer and used by the player.:
        self.__update_used_values(DELETE_INSTANCE, msg);

        msg['destAddr'] = '';
        msg['retId'   ] = '';

        ## LOG:
        self.__print.show('END DEL RECV','I');
        return msg;



    ##
    ## BRIEF: get the resources info to specfic division.
    ## ------------------------------------------------------------------------
    ## @PARAM int division.
    ##
    def __get_resources_inf(self, division):

        ## LOG:
        self.__print.show('GET RESOURCES FROM DISIONS LEQ '+str(division), 'I');

        resources = {};

        ## Select all player from divisions: 
        dRecv=self.__db.all_regs_filter(Player, (Player.division <= division));

        if dRecv != []:
            values = [0, 0, 0, 0, 0, 0];

            for player in dRecv:
                 values[0] += int(player['vcpus'        ]);
                 values[1] += int(player['vcpus_used'   ]);
                 values[2] += int(player['local_gb'     ]);
                 values[3] += int(player['local_gb_used']);
                 values[4] += int(player['memory'       ]);
                 values[5] += int(player['memory_used'  ]);

            resources['vcpus'        ] = values[0];
            resources['vcpus_used'   ] = values[1];
            resources['local_gb'     ] = values[2];
            resources['local_gb_used'] = values[3];
            resources['memory'       ] = values[4];
            resources['memory_used'  ] = values[5];

        return resources;


    ##
    ## BRIEF: set the resources info to specfic division.
    ## ------------------------------------------------------------------------
    ## @PARAM int division ==.
    ## @PARAM dict msg     == message data.
    ##
    def __set_resources_inf(self, division, msg):

        ## LOG:
        self.__print.show('UPDATE RESOURCE TABLE: ' + str(msg), 'I');

        ## Get all data from the message. Vcpus, memory and disk avaliable in
        ## the player:
        data = {
            'name'     : msg['playerId'],
            'vcpus'    : msg['data']['vcpus'   ],
            'memory'   : msg['data']['memory'  ],
            'local_gb' : msg['data']['local_gb']
        };

        self.__db.update_reg(Player, Player.name == msg['playerId'], data);

        return {};


    ##
    ## BRIEF: choice the best player to perform the request.
    ## ------------------------------------------------------------------------
    ## @PARAM int division == division to considerated.
    ## @PARAM str playerId == player's id who made the request.
    ##
    def __get_player(self, division, playerId):
       selectedPlayer = {};

       ## Genereate the query to select the players belong to specific division.
       fColumns = and_(Player.division >= division, 
                       Player.name     != playerId,
                       Player.enabled  == 1);

       dRecv = self.__db.all_regs_filter(Player, fColumns);

       ## Print all player able to execute the request.
       self.__show_all_player_candidates(dRecv);

       if dRecv != []:
           ## Perform the player selection. Utilize the scheduller algorithm se
           ## lected before.
           selectedPlayer = self.__scheduller.run(dRecv);

       ## LOG:
       self.__print.show('PLAYER SELECTED: ' + str(selectedPlayer), 'I');

       return selectedPlayer;


    ##
    ## BRIEF: print all player able to execute the request.
    ## ------------------------------------------------------------------------
    ## @PARAM players == list of players.
    ## 
    def __show_all_player_candidates(self, players):

        for player in players:
            ## LOG:
            self.__print.show(str(player), 'I');

        return SUCCESS;


    ##
    ## BRIEF: get information about an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == message with some datas about instance.
    ##
    def __get_instance_info(self, message):
        ## TODO: if the instance is not running decrement table values!
        return SUCCESS;


    ##
    ## BRIEF: update all values of offer and used resources by division. 
    ## ------------------------------------------------------------------------
    ## @PARAM int  action  == increment (0) or decrement (1) usage.
    ## @PARAM dict message == message with some datas about instance.
    ##
    def __update_used_values(self, action, msg):

        ## LOG:
        self.__print.show('UPDATE - ACTION: ' +str(action)+ ' ' +str(msg), 'I');
        
        ## Perform a select to get all vm instances assign (running) in vPlayer.
        dRecv=self.__db.all_regs_filter(Player,(Player.name == msg['destName']));

        if dRecv != []:
            ## LOG:
            self.__print.show('UPDATE: VALRET: ' + str(dRecv), 'I');

            ## Set all data to update the player status.
            data = {};

            ## When action is equal the 0 meaning that the values will be incre
            ## mented (create instance). 1 is decremented (delete instance)!
            if   action == CREATE_INSTANCE:
                data = self.__increment_value_database(dRecv[-1], msg);

            elif action == DELETE_INSTANCE:
                data = self.__decrement_value_database(dRecv[-1], msg);

            self.__db.update_reg(Player, Player.name == msg['destName'], data);

        return SUCCESS;


    ##
    ## BRIEF: increment player values.
    ## ------------------------------------------------------------------------
    ## @PARAM recv == values to update.
    ## @PARAM msg  == message received.
    ##
    def __increment_value_database(self, recv, msg):

        record = {};

        ## Convert values:
        record['vcpus_used'   ] = int(recv['vcpus_used'   ]);
        record['memory_used'  ] = int(recv['memory_used'  ]);
        record['local_gb_used'] = int(recv['local_gb_used']);
        record['accepts'      ] = int(recv['accepts'      ]);
        record['running'      ] = int(recv['running'      ]);
        record['rejects'      ] = int(recv['rejects'      ]);

	if msg['status'] == SUCCESS:
            record['vcpus_used'   ] += int(msg['data']['vcpus']);
            record['memory_used'  ] += int(msg['data']['mem'  ]);
            record['local_gb_used'] += int(msg['data']['disk' ]);
            record['accepts'      ] += 1;
            record['running'      ] += 1;
        else:
            record['rejects'      ] += 1;

        ## LOG:
        self.__print.show('VALUES UDPATE AFTER DEL' + str(record),'I');

        return record;


    ##
    ## BRIEF: decrement player values.
    ## ------------------------------------------------------------------------
    ## @PARAM recv == values to update.
    ## @PARAM msg  == message received.
    ##
    def __decrement_value_database(self, recv, msg):

        record = {};

        ## Convert values:
        record['vcpus_used'   ] = int(recv['vcpus_used'   ]);
        record['memory_used'  ] = int(recv['memory_used'  ]);
        record['local_gb_used'] = int(recv['local_gb_used']);
        record['running'      ] = int(recv['running'      ]);
        record['finished'     ] = int(recv['finished'     ]);
        record['problem_del'  ] = int(recv['problem_del'  ]);

        if msg['status'] == SUCCESS:

           record['vcpus_used'   ] -= int(msg['data']['vcpus']);
           record['memory_used'  ] -= int(msg['data']['mem'  ]);
           record['local_gb_used'] -= int(msg['data']['disk' ]);
           record['running'      ] -= 1;
           record['finished'     ] += 1;
        else:
            record['problem_del'] += 1;

        ## LOG:
        self.__print.show('VALUES UDPATE AFTER DEL' + str(record),'I');

        return record;
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
        self.__logger = self.__logger_setting(self.__cfg['log']);


    ###########################################################################
    ## PUBLIC                                                                ##
    ###########################################################################
    ##
    ## BRIEF: start the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def start(self):
        self.__running = MCT_Referee(self.__cfg, self.__logger);
        self.__running.consume();
        return SUCCESS;


    ##
    ## BRIEF: stiop the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        self.__running.stop();
        return SUCCESS;


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

## END CLASS.








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
## EOF.
