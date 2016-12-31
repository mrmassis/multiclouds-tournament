#!/usr/bin/env python








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
import time;
import sys;
import os;
import datetime;
import ConfigParser;
import logging;
import logging.handlers;

from mct.lib.utils    import *;
from mct.lib.database import MCT_Database;
from multiprocessing  import Process, Queue, Lock;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE   = '/etc/mct/mct-divisions.ini';
LOG_NAME      = 'MCT_Divisions';
LOG_FORMAT    = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME  = '/var/log/mct/mct_divisions.log';








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
    __interval     = None;
    __index        = None;
    __round        = None;
    __dbConnection = None;
    __lock         = None;
    __print        = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM dict dbConnection == database connection with locker.
    ## @PARAM dict cfg          == dictionary with MCT_Agent configs.
    ## @PARAM obj  logger       == logger object.
    ##
    def __init__(self, cfg, dbConnection, logger):
        super(Division, self).__init__(name=self.name);

        self.__dbConnection = dbConnection;

        ## Obtain the loop interval, the division index and the round time from
        ## division.
        self.__interval = cfg['interval'];
        self.__index    = cfg['number'  ];
        self.__round    = cfg['round'   ];
        
        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['print'], logger)

        ## LOG:
        self.__print.show('INITIALIZE DIVISION ' + self.name, 'I');


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

            if divmod(eT.total_seconds(),60)[0] >= int(self.__round):

                 ## LOG:
                 self.__print.show(self.name + ' ROUND FINISHED!', 'I');

                 ## Calculates attributes (score and history) of each player in
                 ## the division.
                 self.__calculate_attributes();

                 timeOld = datetime.datetime.now();

            time.sleep(float(self.__interval));

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
        logger.info("CALC ATTRIBUTES TO PLAYER FROM DIVISION: %s", self.name);

        ## Generate the query to get all players belong to division of interest.
        query  = 'SELECT name, score, historic FROM PLAYER ';
        query += "WHERE division='"+ self.__index + "'";

        self.__dbConnection['lock'].acquire();
        valRet = [] or self.__dbConnection['dbase'].select_query(query);
        self.__dbConnection['lock'].relase();

        ## Convert the query's result (string) to the python dictionary format.
        attributesPlayers = [];
        for player in valRet:

            ## Get the last idx from REQUEST table that will be considerated to
            ## get request results.
            query  = "SELECT idx FROM LAST_IDX ";
            query += "WHERE division='" + self.__index + "'";

            self.__dbConnection['lock'].acquire();
            index = self.__dbConnection['dbase'].select_query(query)[0][0];
            self.__dbConnection['lock'].relase();

            ## Get all request from a player. The result considers all requests
            ## before the idx.
            query  = "SELECT * FROM REQUEST ";
            query += "WHERE ";
            query += "player_id='"+ player[0] +"' and id >='"+ str(index)+"' ";

            self.__dbConnection['lock'].acquire();
            valRet = [] or self.__dbConnection['dbase'].select_query(query);
            self.__dbConnection['lock'].relase();

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

                self.__dbConnection['lock'].acquire();
                valRet = self.__dbConnection['base'].update_query(query);
                self.__dbConnection['lock'].relase();
                
                query  = "UPDATE LAST_IDX SET "
                query += "idx='"            +str(nIndex)  + "' ";
                query += "WHERE divison='" + self.__index + "' ";
                
                self.__dbConnection['lock'].acquire();
                valRet = self.__dbConnection['dbase'].update_query(query);
                self.__dbConnection['lock'].relase();

        return 0;


    ##
    ## BRIEF: calculate a new player's score. 
    ## ------------------------------------------------------------------------
    ## @PARAM float oldScore == the score before update.
    ## 
    def __calculate_score(self, oldScore):
        ## TODO:
        ## para cada player deve-se obter as acoes de interesse (aceitar) a
        ## requisicao de instancias. 
        ## deve ser considerada a divisao atual, e o ultimo  checkpoint de
        ## round.
        ## LOG:
        self.__print.show(self.name + ' CALCULATE SCORE!', 'I');
        return oldScore;


    ##
    ## BRIEF: calculate a new player's historic.
    ## ------------------------------------------------------------------------
    ## @PARAM float oldHistoric == the historic before update.
    ## 
    def __calculate_histc(self, oldHistc):
        ## TODO:
        ## obter a media do score da divisao.
        ## LOG:
        self.__print.show(self.name + ' CALCULATE HISTORIC!', 'I');
        return oldHistc;
## END CLASS.








class MCT_Divisions:

    """
    Class MCT_Referee: start and mantain the MCT referee.
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    ** run            == main loop.
    ** gracefull_stop == grecefull finish the divisions.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __threadsId = None;
    __interval  = None;
    __print     = None;


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

        ## LOG:
        self.__print.show('INITIALIZE MCT_DIVISIONS!', 'I');

        ## Intance a new object to handler all operation in the local database
        dbConnection = {
            'dbase': MCT_Database(cfg['database']),
            'lock' : Lock()
        }

        ## Time to waiting until next loop:
        self.__interval = cfg['main']['interval'];

        ## Create all threads. The number of threads are defineds in the conf.
        ## file.
        for divNumb in range(1, int(cfg['main']['num_divisions']) + 1):
            name = 'division' + str(divNumb);

            division = Division(cfg[name], dbConnection, logger);
            division.name   = name;
            division.daemon = True;
            division.start();

            self.__threadsId.append(division);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):
        while True:
            time.sleep(float(self.__interval));
            
            ## TODO:
            ## Check the sanity of the divisions' thread (is running?).

        return 0;


    ##
    ## BRIEF: grecefull finish the divisions.
    ## ------------------------------------------------------------------------
    ##
    def gracefull_stop(self):

        for thread in self.__threadsId:
            thread.terminate();
            thread.join();

        ## LOG:
        self.__print.show('GRACEFULL STOP...', 'I');
        return 0;
## END.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    ## Get all configs parameters presents in the config file localized in
    ## CONFIG_FILE path.
    cfg = get_configs(CONFIG_FILE);

    try:
        mctDivisions = MCT_Divisions(cfg, logger);
        mctDivisions.run();

    except KeyboardInterrupt, error:
        mctDivisions.gracefull_stop();

    sys.exit(0);
## EOF.

