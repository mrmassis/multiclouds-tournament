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

from mct.lib.database_sqlalchemy  import MCT_Database_SQLAlchemy, Simulation;
from mct.lib.utils                import *;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE      = '/etc/mct/mct-db-proxy.ini';
LOG_NAME         = 'MCT_Db_Proxy';
LOG_FORMAT       = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME     = '/var/log/mct/mct_db_proxy.log';
SIMULATION_TABLE = 'SIMULATION'
ADD_VM_INSTANCE  = 0
DEL_VM_INSTANCE  = 1
INF_VM_INSTANCE  = 2
SOCKET_PORT      = 10000
T_T_MIN          = 0.0
T_T_MAX          = 0.3
T_S_MIN          = 0.3
T_S_MAX          = 0.6
T_B_MIN          = 0.6
T_B_MAX          = 1.1
TIME_BASE        = 3277 ## 3277837725 microseconds: timestamp from first entry.







###############################################################################
## LOG                                                                       ##
###############################################################################
## Create a handler and define the output filename and the max size and max nun
## ber of the files (1 mega = 1048576 bytes).
handler= logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                              maxBytes=10485760,
                                              backupCount=100);

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
    __count    = 1;
    __db       = None;
    __state    = {};
    __tmpTable = None;
    __port     = SOCKET_PORT
    __print    = None;
    __sTable   = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, cfg):

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## Intance a new object to handler all operation in the local database.
        self.__db = MCT_Database_SQLAlchemy(cfg['database']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: execute main loop to waiting connections.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        ## LOG:
        self.__print.show("\n########## START MCT_DB_PROXY ##########\n",'I');

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

           ## Convert the return value of the authentication from simple dictio
           ## nary format to json format.
           messageJsonSend = json.dumps(messageDictSend, ensure_ascii=False);

           connection.sendall(messageJsonSend);
           connection.close();

           ## LOG:
           self.__print.show('END OF REQUEST!\n---', 'I');

           if messageDictSend['valid'] == 2:
               ## LOG:
               self.__print.show('THE ACTIONS FINISH, DATABASE EMPTY!!!', 'I');
               break;

        return 0;


    ##
    ## BRIEF: finish execution.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):

        ## LOG:
        self.__print.show("\n########## FINISH MCT_DB_PROXY ##########\n",'I');

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
            if data['valid'] == 0 and data['action'] != INF_VM_INSTANCE:

                ## The machineID received from database through 'MCT_DB_Proxy'.
                machineId = data['machineID'];

                ## Case the action is to create a VM, return the action's data.
                if data['action'] == ADD_VM_INSTANCE:

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
            'valid':1
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
        actionData = {'valid':2};

        filterDict = {
            0 : Simulation.id == idx
        };

        dataReceived=self.__db.first_reg_filter(Simulation, filterDict);

        if dataReceived != []:

            ## Fields: 0) id, 1) time, 2) machineId, 3) eventType, 4) plataform
            ## Id, 5) cpu, 6) memory, and 7) valid.
            actionData['id'       ] =   int(dataReceived[0]['id'       ]);
            actionData['machineID'] =   int(dataReceived[0]['machineId']);
            actionData['action'   ] =   int(dataReceived[0]['eventType']);
            actionData['time'     ] =   int(dataReceived[0]['time'     ]);
            actionData['valid'    ] =   int(dataReceived[0]['valid'    ]);
            actionData['cpu'      ] = float(dataReceived[0]['cpu'      ]);
            actionData['mem'      ] = float(dataReceived[0]['memory'   ]);

            ## Convert time from microseconds to seconds. Normalize the time too
            actionData['time'] = int(actionData['time']/1000000) - TIME_BASE;

            ## Case the action is to create a new vm instance, check the type of
            ## instance:
            if actionData['action'] == ADD_VM_INSTANCE:
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
        if   memFactor >= T_T_MIN and memFactor < T_T_MAX:
            vmType = 'T';

        elif memFactor >= T_S_MIN and memFactor < T_S_MAX:
            vmType = 'S';

        elif memFactor >= T_B_MIN and memFactor < T_B_MAX:
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








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    try:
        ## Get from configuration file all players and all respective paramters
        cfg = get_configs(CONFIG_FILE);

        proxy_db_server = MCT_DB_Proxy(cfg);
        proxy_db_server.run();

    except KeyboardInterrupt:
        proxy_db_server.stop();

    sys.exit(0);
## EOF.
