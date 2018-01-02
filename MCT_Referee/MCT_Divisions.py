#!/usr/bin/env python


import time;
import sys;
import os;
import datetime;
import ConfigParser;
import logging;
import logging.handlers;

from mct.lib.utils               import *;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy, Player, Vm, Status;
from multiprocessing             import Process, Queue, Lock;





###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE           = 'mct-divisions.ini';
HOME_FOLDER           = os.path.join(os.environ['HOME'], CONFIG_FILE);
RUNNING_FOLDER        = os.path.join('./'              , CONFIG_FILE);
DEFAULT_CONFIG_FOLDER = os.path.join('/etc/mct/'       , CONFIG_FILE);












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
    __print = None;
    __db    = None;
    __id    = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, cfg, db, logger):
        super(Division, self).__init__(name=dName);

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(vCfg['print'], logger);

        ## Get the identification number (id) of division.
        self.__id = cfg['id'  ];

        ## Get loop waiting interval. This value determine the time to waiting
        ## between the loops.
        self.__interval = float(cfg['interval']);

        ## Get the round value. At end of this value the system compute the pla
        ## eyrs attributes.
        self.__round = int(cfg['round']);

        ## LOG:
        self.__print.show('INITIALIZE DIVISION: ' + self.__id, 'I');

        ## Setting the database attribute. In this attribute are the db connec-
        ## tion and the lock to avoid data corruption.
        self.__db = db;

        ## Get time running threshold:
        self.__timeThreshold = int(cfg['threshold']);


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

            ## Obtain the current time.
            timeNow = datetime.datetime.now();

            ## Elapsed time of the last "round". Used to verify the next round.
            eT = timeNow - timeOld;

            if divmod(eT.total_seconds(),60)[0] >= self.__round:

                 ## LOG:
                 self.__print.show('ROUND FINISHED AT DIV: '+str(self.__id),'I');

                 ## Calculate attributes (score|hist) of each player in the div.
                 self.__calculate_attributes();

                 timeOld = datetime.datetime.now();

            time.sleep(self.__interval);

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
        self.__print.show('CALC PLAYER ATTRIBS FROM DIV: '+str(self.__id),'I');

        ## Select all player belongs at division self.__id (1, 2, 3, 4 ..., n);
        fColumns = (Player.division == self.__id);

        self.__db['lock'].acquire();
        dRecv = self.__db['db'  ].all_regs_filter(Player, fColumns);
        self.__db['lock'].release();

        if dRecv != []:

            ## To each player belong to division self.__id calculate the attri-
            ## butes (scores, history etc).
            for player in dRecv:

                invidualFairness = 0.0;

                nScore = self.__calculate_score(player);
                nHistc = self.__calculate_histc(player);
                nFairn = self.__calculate_fairn(player);

                ## TODO: CHECK DIVISION:

                data = {
                    'name'    : player['name'],
                    'score'   : nScore,
                    'history' : nHistc,
                    'fairness': nFairn
                }

                ##
                fColumns = (Player.name == player['name']);

                self.__db['lock'].accquire();
                self.__db['db'  ].update_reg(Player, fColumns, data)
                self.__db['lock'].release();

        return 0;


    ##
    ## BRIEF: calculate a new player's score. 
    ## ------------------------------------------------------------------------
    ## @PARAM player == player data dictionary.
    ## 
    def __calculate_score(self, player):
        nScore = 0.0;

        return nScore;


    ##
    ## BRIEF: calculate a new player's historic.
    ## ------------------------------------------------------------------------
    ## @PARAM player == player data dictionary.
    ## 
    def __calculate_histc(self, player):
        nHistory = 0;

        return nHistory;


    ##
    ## BRIEF: calculate player fairness.
    ## ------------------------------------------------------------------------
    ## @PARAM player == player data dictionary.
    ## 
    def __calculate_fairn(self, player):

        fairness = 0.0;
        accepts  = 0;
        rejects  = 0;
        requests = 0;

        ## Obtain all entries from VM table:
        fColumn = (Vm.origin_name == player['name']);

        self.__db['lock'].accquire();
        dRecv = self.__db['db'].all_regs_filter(Vm, fColumn);
        self.__db['lock'].release();

        if dRecv != []:
            requests = len(dRecv);

            for request in dRecv:

                if  request['status'] == FINISHED:
                    tsIni = dRecv['timestamp_received'];
                    tsEnd = dRecv['timestamp_finished'];

                    ## Calculate the time of the instance is running. Accept the
                    ## instance only the time is under the threadshold.
                    tRunSecs = calculate_time(tsIni, tsEnd);
                    
                    if tRunSecs > self.__timeThreshold or tRunSecs < 0.0:
                        accpets += 1;
                    else:
                        rejects += 1;

                elif request['status'] == SUCCESS :
                    accepts += 1;
                else:
                    rejects += 1;

        return fairness;
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
    __threadsId = [];
    __db        = None;
    __logger    = None;
    __divCfgs   = [];
    __print     = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM cfg    == configuration dictionary.
    ## @PARAM logger == log object.
    ## 
    def __init__(self, cfg, logger):

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## LOG:
        self.__print.show('INITIALIZE DIVISIONS', 'I');

        ## Get the configurations related to the execution of the divisions de
        ## fined by the User.
        self.__logger = logger;

        ## Get all division configurations:
        div = 1;
        try:
            self.__divCfgs.append(cfg['division' + str(div)]);
            div += 1;
        except:
            pass;

        ## Intance a new object to handler all operation in the local database.
        self.__db = {
            'db'  : MCT_Database(cfg['database']),
            'lock': Lock()
        };

        ## Get time running threshold:
        self.__timeThreshold = int(cfgi['main']['threshold']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        ## Create all threads.The number of threads are defineds in the cfgFile.
        for divCfg in self.__divCfgs:
            self.start(divCfg);

        self.__waiting_finish();
        return SUCCESS;


    ##
    ## BRIEF: start a thread.
    ## ------------------------------------------------------------------------
    ## @PARAM divCfg == thread configuration.
    ##
    def start(self, divCfg):
        ## LOG:
        self.__print.show('START A NEW DIVISION IN THE MCT', 'I');

        ## Start the new division running in thread.
        newDivision = Division(divCfg, self.__db, self.__logger);
        newDivision.daemon = True;
        newDivision.start();

        ## Store the thread:
        self.__threadsId.append(newDivision);
        return SUCCESS;


    ##
    ## BRIEF: grecefull finish the divisions.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        for thread in self.__threadsId:
            thread.terminate();
            thread.join();

        ## LOG:
        self.__print.show('GRACEFULL STOP', 'I');
        return SUCCESS;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: wait threads finish.
    ## ------------------------------------------------------------------------
    ##
    def __waiting_finish(self):

        while True:
            ## LOG:
            self.__print.show('CALCULATE THE GLOBAL FAIRNESS', 'I');

            ## Calculate global fairness:
            self.__calculate_global_fairness();

            ## Wait 5 minutes:
            time.sleep(300);

        for thread in self.__threadsId:
            thread.join();
 
        ## LOG:
        self.__print.show('FINISHED', 'I');
        return SUCCESS;


     ##
     ## BRIEF: calculate the global fairness.
     ## -----------------------------------------------------------------------
     ## 
     def __calculate_global_fairness(self):
          globalFairness = 0.0;

          accepts = 0;
          rejects = 0;
          allReqs = 0;

          ## Obtain all entries from VM table:
          self.__db['lock'].accquire();
          dRecv = self.__db['db'].all_regs(Vm);
          self.__db['lock'].release();

          if dRecv != []:

              ## Obtain the number of the all request by create new instances.
              allReqs = len(dRecv);

              ## Iteract throw the records.
              for vm in dRecv:

                  ## LOG:
                  self.__print.show('REQUEST: ' + str(vm), "I");

                  ## If the vm is finished or running they were accepts.
                  if  vm['status'] == FINISHED:
                    tsIni = vm['timestamp_received'];
                    tsEnd = vm['timestamp_finished'];

                    ## Calculate the time of the instance is running. Accept the
                    ## instance only the time is under the threadshold.
                    tRunSecs = calculate_time(tsIni, tsEnd);

                    if tRunSecs > self.__timeThreshold or tRunSecs < 0.0;
                        accpets += 1;
                    else:
                        rejects += 1;

                elif request['status'] == SUCCESS :
                    accepts += 1;
                else:
                    rejects += 1;

              ## Calculate:
              try:
                  globalFairness = float(accepts) / float(allReqs);
              except:
                  globalFairness = 0.0;
 
          ## Update in table STATUS:
          data = {
              'all_requests': allReqs,
              'accepts'     : accepts,
              'rejects'     : rejects,
              'fairness'    : globalFairness,
              'timestamp'   : str(datetime.datetime.now()) 
          }

          self.__db['lock'].accquire();
          self.__db['db'  ].update_reg_without_filter(Status, data);
          self.__db['lock'].release();
              
          ## LOG:
          self.__print.show('GLOBAL FAIRNESS: ' + str(globalFairness), "I");
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
        self.__logger = self.__logger_setting(self.__cfg['log']);


    ###########################################################################
    ## PUBLIC                                                                ##
    ###########################################################################
    ##
    ## BRIEF: start the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def start(self):
        self.__running = MCT_Divisions(self.__cfg, self.__logger);
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

