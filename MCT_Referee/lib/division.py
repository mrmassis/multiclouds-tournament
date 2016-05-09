#!/usr/bin/env python


import pika;
import time;
import sys;
import os;
import datetime;
import ConfigParser;
import json;
import logging;
import logging.handlers;

from lib.database     import Database;
from multiprocessing  import Process, Queue, Lock;





###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE   = '/etc/mct/mct_referee.ini';
LOG_NAME      = 'MCT_Referee';
LOG_FORMAT    = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME  = '/var/log/mct/mct_referee.log';








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
class Division(Process):

    """
    Class Division:
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    * run == division main loop.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __dNumb = None;
    __dName = None;
    __dConf = None;
    __dBase = None;
    __dLock = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, dNumb, dName, dConf, dBase, dLock):
        super(Division, self).__init__(name=dName);

        self.__dNumb = dNumb;
        self.__dName = dName;
        self.__dConf = dConf;
        self.__dBase = dBase;
        self.__dLock = dLock;

        ## LOG:
        logger.info('STARTED DIVISION %s', dName);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## Brief: division main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        ## Obtain the initial base used to check when will be held the round 1.
        timeOld = datetime.datetime.now();

        while True:

            ## Obtain the current time. The value is used to calculate the time
            ## difference.
            timeNow = datetime.datetime.now();

            ## Elapsed time of the last round until now. Used to check the next
            ## round.
            eT = timeNow - timeOld;

            if divmod(eT.total_seconds(),60)[0] >= int(self.__dConf['round']):
                 ## LOG:
                 logger.info('ROUND FINISHED!');

                 ## Calculates attributes (score and history) of each player in
                 ## the division.
                 #self.__calculate_attributes();

                 timeOld = datetime.datetime.now();

            time.sleep(float(self.__dConf['steep']));

        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: Calculate attributes of each player in the  division.
    ## ------------------------------------------------------------------------
    ## 
    def __calculate_attributes(self):
        ## LOG:
        logger.info("CALC ATTRBS TO PLAYER FROM DIVISION: %s", self.__dName);

        ## Generate the query to get all players belong to division of interest.
        query  = 'SELECT name, score, historic FROM PLAYER ';
        query += "WHERE division='"+ str(self.__dNumb) + "'";

        self.__dLock.acquire();
        valRet = [] or self.__dBase.select_query(query);
        self.__dLock.release();

        ## Convert the query's result (string) to the python dictionary format.
        attributesPlayers = [];
        for player in valRet:

            ## Get the last idx from REQUEST table that will be considerated to
            ## get request results.
            query  = "SELECT idx FROM LAST_IDX ";
            query += "WHERE division='" + str(self.__dNumb) + "'";

            self.__dLock.acquire();
            index = self.__dBase.select_query(query)[0][0];
            self.__dLock.release();

            ## Get all request from a player. The result considers all requests
            ## before the idx.
            query  = "SELECT * FROM REQUEST ";
            query += "WHERE ";
            query += "player_id='"+ player[0] +"' and id >='"+ str(index)+"' ";

            self.__dLock.acquire();
            valRet = [] or self.__dBase.select_query(query);
            self.__dLock.release();

            if valRet == []:
                ## Get the last ID obtained from query:
                nIndex = 0 

                nScore = self.__calculate_score(player[1]);
                nHistc = self.__calculate_histc(player[2]);
                nDivis = 1;
                
                query  = "UPDATE PLAYER SET ";
                query += "score='"      + str(nScore)    + "', ";
                query += "historic='"   + str(nHistc)    + "', ";
                query += "division='"   + str(nDivis)    + "', ";
                query += "WHERE name='" + str(player[0]) + "'  ";
                
                print query

                #self.__dLock.acquire();
                #valRet = self.__dBase.update_query(query);
                #self.__dLock.release();
                #
                query  = "UPDATE LAST_IDX SET "
                query += "idx='"            +str(nIndex)       + "' ";
                query += "WHERE divison='" + str(self.__dNumb) + "' "; 

                print query
                #
                #self.__dLock.acquire();
                #valRet = self.__dBase.update_query(query);
                #self.__dLock.release();

        return 0;


    ##
    ## BRIEF: 
    ## ------------------------------------------------------------------------
    ## 
    def __calculate_score(self, oldScore):
        ## TODO:
        ## para cada player deve-se obter as acoes de interesse (aceitar) a
        ## requisicao de instancias. 
        ## deve ser considerada a divisao atual, e o ultimo  checkpoint de
        ## round.
        ## LOG:
        logger.info("CALCULATE SCORE");
        return oldScore;


    ##
    ## BRIEF: 
    ## ------------------------------------------------------------------------
    ## 
    def __calculate_histc(self, oldHistc):
        ## TODO:
        ## obter a media do score da divisao.
        ## LOG:
        logger.info("CALCULATE HISTC");
        return oldHistc;
## EOF.

