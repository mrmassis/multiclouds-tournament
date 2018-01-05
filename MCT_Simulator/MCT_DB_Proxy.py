#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
import ConfigParser;
import hashlib;
import time;
import ast;
import logging;
import logging.handlers;
import sys;
import socket;
import json;
import os;

from mct.lib.database_sqlalchemy  import MCT_Database_SQLAlchemy, Simulation;
from mct.lib.utils                import *;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE           = 'mct-db-proxy.ini';
HOME_FOLDER           = os.path.join(os.environ['HOME'], CONFIG_FILE);
RUNNING_FOLDER        = os.path.join('./'              , CONFIG_FILE);
DEFAULT_CONFIG_FOLDER = os.path.join('/etc/mct/'       , CONFIG_FILE);








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_DB_Proxy:

    """
    Class MCT_DB_Proxy_Server: control the database access. 
    --------------------------------------------------------------------------
    PUBLIC METHODS:
    ** run  == listen new requests.
    ** stop == finish the execution. 
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __count      = 1;
    __db         = None;
    __state      = {};
    __port       = None;
    __print      = None;
    __newVMCount = None;
    __tBase      = None;
    __tMin       = None;
    __tMax       = None;
    __sMin       = None;
    __sMax       = None;
    __bMin       = None;
    __bMax       = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM cfg    == configuration dictionary.
    ## @PARAM logger == log object.
    ##
    def __init__(self, cfg, logger):

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## Intance a new object to handler all operation in the local database.
        self.__db = MCT_Database_SQLAlchemy(cfg['database']);

        ## Socket port that the SGDB is listen:
        self.__port = cfg['database']['port'];

        ## This value ensure that the entry is valid. The simulation has valid
        ## entry after the tBase value.
        self.__tBase = int(cfg['main']['time_base']);

        ## Thresholds:
        self.__tMin = float(cfg['threshold']['t_min']);
        self.__tMax = float(cfg['threshold']['t_max']);

        self.__sMin = float(cfg['threshold']['s_min']);
        self.__sMax = float(cfg['threshold']['s_max']);

        self.__bMin = float(cfg['threshold']['b_min']);
        self.__bMax = float(cfg['threshold']['b_max']);

        ## Count.
        self.__newVMCount = 0;


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: execute main loop to waiting connections.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        ## LOG:
        self.__print.show("########## START MCT_DB_PROXY ##########\n",'I');

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);

        s.bind(('', int(self.__port)));
        s.listen(5);

        while True:

           ## LOG:
           self.__print.show('WAIT FOR A REQUEST BY NEW REQUEST!!!', 'I');

           ## Wait new connections from the MCT_Agents. Wait for new request by
           ## authentication.
           connection, address = s.accept();

           ## LOG:
           self.__print.show('NEW RESQUEST FROM: ' + str(address), 'I');

           ## Get messagem from MCT_Agents that wish authenticate and enter in
           ## multiclouds tournament.
           messageJsonRecv = connection.recv(1024);

           ## Load the message - convert from json format to simple dictionary.
           messageDictRecv = json.loads(messageJsonRecv);

           ## Get an action:
           messageDictSend = self.__get_action(messageDictRecv['player']);

           ## LOG:
           self.__print.show('ACTION: ' + str(messageDictSend['action']), 'I');

           ## Convert the return value of the authentication from simple dictio
           ## nary format to json format.
           messageJsonSend = json.dumps(messageDictSend, ensure_ascii=False);

           connection.sendall(messageJsonSend);
           connection.close();

           ## LOG:
           self.__print.show('END OF REQUEST!\n---', 'I');

           if messageDictSend['valid'] == 2:
               ## LOG:
               self.__print.show('DB EMPTY! VMS: '+str(self.__newVMCount), 'I');
               break;

        return 0;


    ##
    ## BRIEF: finish execution.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):

        ## LOG:
        self.__print.show("########## FINISH MCT_DB_PROXY ##########\n",'I');
        return 0


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: get an action from database.
    ## ------------------------------------------------------------------------
    ## @PARAM player == player name.
    ##
    def __get_action(self, player):

        ## Check if already exist an entry in the data list to the request pla-
        ## yer. If dont exist, create a new one.
        self.__list_player(player);

        while True:

            ## Obtain a new action data from dbase through MCT_DB_Proxy service.
            data = self.__get_next_action(self.__state[player]['count']);

            ## After to obtain the new action from database increment the count.
            self.__state[player]['count'] += 1;

            ## Accept only two actions: create a new instance and delete a exis
            ## tent instance in MCT.
            if data['valid'] == 0 and data['action'] != GETINF_INSTANCE:

                ## The machineID received from database through 'MCT_DB_Proxy'.
                machineId = data['machineID'];

                ## Case the action is to create a VM, return the action's data.
                if data['action'] == CREATE_INSTANCE:
                    self.__newVMCount += 1;

                    ## Invalid (set with valid = 1) the used action that id is:
                    self.__invalid_action(self.__state[player]['count']-1);

                    ## Insert the "machine ID" value to the "state dictionary".
                    self.__state[player]['machineID'].append(machineId);
                    break;

                ## Case the action is not to create a new instance,check if the
                ## action is about a job present in the player's state. If yes,
                ## return the action. Otherwise, request a new action.
                if machineId in self.__state[player]['machineID']:

                    ## Invalid (set with valid = 1) the used action that id is:
                    self.__invalid_action(self.__state[player]['count']-1);
        
                    ## Remove the machine ID entry from the "state dictionary".
                    self.__state[player]['machineID'].remove(machineId);
                    break;

            elif data['valid'] == 2:
                break;

        return data;


    ##
    ## BRIEF: invalid the action entry in database.
    ## ------------------------------------------------------------------------
    ## @PARAM idx == index to the action.
    ##
    def __invalid_action(self, idx):

        fieldsToUpdate = {
            'valid' : 1
        };

        ## Update the entry:
        self.__db.update_reg(Simulation, Simulation.id == idx,fieldsToUpdate);

        return 0;


    ##
    ## BRIEF: get next database (action) entry.
    ## ------------------------------------------------------------------------
    ## @PARAM idx == index to get the action.
    ##
    def __get_next_action(self, idx):

        ## If the valid is equal 2, meaning that there isnt record in database.
        ## action 666 :|
        actionData = {'action': 666, 'valid' : 2};

        dRecv = self.__db.all_regs_filter(Simulation, Simulation.id == idx);

        if dRecv != []:

            actionData['id'       ] =   int(dRecv[0]['id'       ]);
            actionData['machineID'] =   int(dRecv[0]['machineId']);
            actionData['action'   ] =   int(dRecv[0]['eventType']);
            actionData['time'     ] =   int(dRecv[0]['time'     ]);
            actionData['valid'    ] =   int(dRecv[0]['valid'    ]);
            actionData['cpu'      ] = float(dRecv[0]['cpu'      ]);
            actionData['mem'      ] = float(dRecv[0]['memory'   ]);

            ## Convert time from microseconds to seconds. Normalize the time too
            actionData['time'] = int(actionData['time']/1000000) - self.__tBase;

            ## Case the action is to create a new vm instance, check the type of
            ## instance:
            if actionData['action'] == CREATE_INSTANCE:
                cpu = actionData['cpu'];
                mem = actionData['mem'];

                ## Mapping schedulling class to virtual machine type inside MCT.
                actionData['vmType'] = self.__get_vm_type(cpu, mem);

        return actionData;


    ##
    ## BRIEF: get the vm type.
    ## ------------------------------------------------------------------------
    ## @PARAM cpuFactor == cpu factor.
    ## @PARAM memFactor == mem factor.
    ##
    def __get_vm_type(self, cpuFactor, memFactor):

        ## VM types: 'T' (tiny), 'S' (Small), and 'B' (Big).
        vmType = '';

        ## Use mem factor to decide which the vm type put inside the request.
        if   memFactor >= self.__tMin and memFactor < self.__tMax:
            vmType = 'T';

        elif memFactor >= self.__sMin and memFactor < self.__sMax:
            vmType = 'S';

        elif memFactor >= self.__bMin and memFactor < self.__bMax:
            vmType = 'B';

        return vmType;


    ##
    ## BRIEF: check if already exist an entry in the data list to the request
    ##        player.
    ## ------------------------------------------------------------------------
    ## @PARAM playerName == name of player.
    ##
    def __list_player(self, playerName):

        if playerName not in self.__state:
             self.__state[playerName] = {
                 'count'     : 1, 
                 'machineID' : []
             };

        return 0;

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
        self.__running = MCT_DB_Proxy(self.__cfg, self.__logger);
        self.__running.run();
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
