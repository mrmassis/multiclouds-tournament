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

from mct.lib.database  import MCT_Database;
from mct.lib.utils     import *;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE   = 'mct_db_proxy.ini';
LOG_NAME      = 'MCT_Db_Proxy';
LOG_FORMAT    = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME  = '/var/log/mct/mct_emulator.log';








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
class MCT_DB_Proxy_Server:

    """
    Class MCT_DB_Proxy_Server: 
    --------------------------------------------------------------------------
    PUBLIC METHODS:
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __count        = 0;
    __dbConnection = None;
    __state        = {};
    __tmpTable     = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, cfg):

        ## LOG:
        LOG.info('[MCT_DB_PROXY] INITIALIZE PROXY DB SERVER!');
       
        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        config = get_configs(CONFIG_FILE);

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = MCT_Database(config['database']);

        ## Create the name of temp table to this simulation:
        self.__tmpTable = 'SIMULATION_DATA' + time.strftime('_%a_%H:%M:%S');

        ## Create a new temporary table and copy SIMULATION table values to its
        self.__dbConnectin.dump_table(config['simulation'], self.__tmpTable);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: execute main loop to waiting connections.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);

        s.bind(('', int(self.__port)));
        s.listen(5);

        while True:
           ## LOG:
           logger.info("WAIT FOR A REQUEST BY NEW REQUEST!!!");

           ## Wait new connections from the MCT_Agents. Wait for new request by
           ## authentication.
           connection, address = s.accept();

           ## LOG:
           logger.info("NEW RESQUEST FROM: " + str(address));

           ## Get messagem from MCT_Agents that wish authenticate and enter in
           ## multiclouds tournament.
           messageJsonRecv = connection.recv(1024);

           ## Load the message - convert from json format to simple dictionary.
           messageDictRecv = json.loads(messageJsonRecv);

           ## Get an action:
           messageDictSend = self.__get_action(messageDictRecv['player']);

           ## Exit condition:
           if messageDictSend == {}:
              break;

           ## Convert the return value of the authentication from simple dictio
           ## nary format to json format.
           messageJsonSend = json.dumps(messageDictSend, ensure_ascii=False);

           connection.sendall(messageJsonSend);
           connection.close();

        return 0;


    ##
    ## BRIEF: finish execution.
    ## ------------------------------------------------------------------------
    ##
    def finish(self):
        ## Delete de temporary simulation table:
        self.__dbConnection.del_table(self.__tmpTable);


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

        ## Get action data from database simulation:
        data = self.__get_next_action(self.__state[player]['count']);

        while data['valid'] != 0:

            ## Set the 'global start counter' to first valid entry in database.
            self.__count += 1;

            while True:

                ## Case the action is to create a VM, return the action's data.
                if data['action'] == CREATE_INSTANCE:
                    self.__state[name]['jobID'].append(actionData['jobID']);

                    ## Invalid the used action!
                    self.__invalid_action(self.__state[player]['count']);
                    return data;

                ## Case the action is not to create a new instance,check if the
                ## action is about a job present in the player's state. If yes,
                ## return the action. Otherwise, request a new action.
                if data['jobID'] in self.__state[player]['jobID']:

                    ## Invalid the used action!
                    self.__invalid_action(self.__state[player]['count']);
                    return data;

                ## After to receive the new action from database increment the
                ## player's count
                self.__state[player]['count'] += 1;

                ## Get action data from database simulation:
                data = self.__get_next_action(self.__state[player]['count']);

        return {};


    ##
    ## BRIEF: invalid the action entry in database.
    ## ------------------------------------------------------------------------
    ## @PARAM idx == index to the action.
    ##
    def __invalid_action(self, idx):

        query  = "UPDATE " + self.__tmpTable  + " SET valid='1' ";
        query += "WHERE idx='" + str(idx) + "' " ;
        valRet = self.__db.update_query(query);

        return 0;


    ##
    ## BRIEF: get next database (action) entry.
    ## ------------------------------------------------------------------------
    ## @PARAM idx == index to get the action.
    ##
    def __get_next_action(self, idx):

        vmTypes = {
            0 : 'T',
            1 : 'S',
            2 : 'B',
            3 : 'B',
        };

        ## Mount the select query: 
        dbQuery  = "SELECT * FROM "+self.__tmpTable+" WHERE idx='" + idx + "'";

        dataReceived = [] or self.__dbConnection.select_query(dbQuery);
 
        if dataReceived != []:
          actionData['jobID' ] = dataReceived[0][1];
          actionData['action'] = dataReceived[0][2];
          actionData['valid' ] = dataReceived[0][4];

          ## Case the action is to create a new vm instance, check the type of
          ## instance:
          if actionData['action'] == CREATE_INSTANCE:
              actionData['vmType'] = vmTypes[dataReceived[0][3]];
        else:
            actionData['valid'] = 1;        

        return actionData;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM playerName == name of player.
    ##
    def __list_player(self, playerName):

        if playerName not in self.__state:
             self.__state[name] = {
                 'count' : self.__count, 
                 'jobId' : []
             };

        return 0;

## END CLASS.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    ## LOG:
    logger.info('EXECUTION STARTED...');

    try:
        ## Get from configuration file all players and all respective paramters
        cfg = get_configs(CONFIG_FILE);

        proxy_db_server = MCT_DB_Proxy(cfg);
        proxy_db_server.run();

    except KeyboardInterrupt:
        proxy_db_server.finish();

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF.
