#!/usr/bin/env python


import sys;
import json;
import logging;
import logging.handlers;
import socket;

from mct.lib.utils    import *;
from mct.lib.database import MCT_Database;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE      = '/etc/mct/mct_bid.ini';
LOG_NAME         = 'MCT_Bid';
LOG_FORMAT       = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME     = '/var/log/mct/mct_bid.log';
MIN_DIVISION     = 3





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
class MCT_Registry:

    """
    Register the new player in the bollentin.
    ---------------------------------------------------------------------------
    listen_connection == wait for new request to player register.
    
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __addr         = None;
    __port         = None;
    __dbConnection = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        configs = get_configs(CONFIG_FILE);

        ## Server parameters:
        self.__addr = configs['connection']['addr'];
        self.__port = configs['connection']['port'];

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = MCT_Database(configs['database']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: liste for the new request to register players.
    ## ------------------------------------------------------------------------
    ##
    def listen_connections(self):

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

           ## Authenticate the player and receive the return: 
           messageDictSend = self.__authenticate(messageDictRecv);

           ## Convert the return value of the authentication from simple dictio
           ## nary format to json format.
           messageJsonSend = json.dumps(messageDictSend, ensure_ascii=False);

           connection.sendall(messageJsonSend);
           connection.close();

        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: receive message from players.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __authenticate(self, message):


       ## LOG:
       logger.info('MESSAGE RECEIVED FROM AGENT: %s', message);

       playerId = message['playerId'];
       address  = message['origAdd' ];
       data     = message['data'    ];

       ## Check if the player always registered in the BID:
       valRet = self.__check_player(playerId);

       if valRet == 1:
           ## Register a new player in the BID (database of player belongs to
           ## the multiclouds tournament).
           valRet = self.__register_player(playerId, address, data);

       message['status'] = 1;

       return message;


    ##
    ## BRIEF: check if the player exist in database.
    ## ------------------------------------------------------------------------
    ## @PARAM str playerId  == identifier of the player.
    ##
    def __check_player(self, playerId):

        ## Check if the line that represent the request already in db. Perform
        ## a select.
        query  = "SELECT * FROM PLAYER WHERE name='" + str(playerId) + "'";
        valRet = [] or self.__dbConnection.select_query(query)

        ## Verifies that the request already present in the requests 'database'
        ## if not insert it.
        if valRet == []:
            ## LOG:
            logger.info('PLAYER ID %s not registered!', playerId);
            return 1;

        return 0;


    ##
    ## BRIEF: register a player in de bid.
    ## ------------------------------------------------------------------------
    ## @PARAM str  playerId == identifier of the player.
    ## @PARAM str  address  == player address.
    ## @PARAM dict data     == data with resources from player.
    ##
    def __register_player(self, playerId, address, data):

        ##
        ## TODO: colocar aqui para definir os atributos iniciais.
        ##

        ## 
        v = data['vcpus' ];
        m = data['memory'];
        d = data['disk'  ];

        try: 
            query  = "INSERT INTO PLAYER (";
            query += "name, ";
            query += "address, ";
            query += "division, ";
            query += "score, ";
            query += "historic, ";
            query += "vcpu, ";
            query += "memory, ";
            query += "disk, ";
            query += "vcpu_used, ";
            query += "memory_used, ";
            query += "disk_used";
            query += ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)";
            value  = (playerId, address, MIN_DIVISION,0.0,0,v,m,d,0,0,0);
            valRet = self.__dbConnection.insert_query(query, value)

        except:
            return 1;
 
        return 0;

    ##
    ## BRIEF: create a new token.
    ## ------------------------------------------------------------------------
    ##
    def __generate_new_token(self, playerId):
        return 0;
## END.







###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    ## LOG:
    logger.info('EXECUTION STARTED...');

    try:
        mct_registry = MCT_Registry();
        mct_registry.listen_connections();

    except KeyboardInterrupt, error:
        pass;

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF.
