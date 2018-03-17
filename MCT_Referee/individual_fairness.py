#!/usr/bin/env python

from __future__                  import with_statement;

import time;
import sys;
import os;
import datetime;
import ConfigParser;
import logging;
import logging.handlers;
import importlib;

from mct.lib.utils               import *;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy, Player, Vm, Status, Threshold, Division;
from multiprocessing             import Process, Queue, Lock;





###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE           = 'mct-divisions.ini';
HOME_FOLDER           = os.path.join(os.environ['HOME'], CONFIG_FILE);
RUNNING_FOLDER        = os.path.join('./'              , CONFIG_FILE);
DEFAULT_CONFIG_FOLDER = os.path.join('/etc/mct/'       , CONFIG_FILE);

PLAYOFF_OUT = 0;
PLAYOFF_IN  = 1;

ATTRIBUTES_MODULE = None;

MANAGER_STEEP = 1








###############################################################################
## CLASSES                                                                   ##
###############################################################################
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
        self.__cfg = self.__get_configs();

        ## Configurate the logger. Use the parameters defineds in configuration
        ## file.
        self.__logger = self.__logger_setting(self.__cfg['log']);

        ## Intance a new object to handler all operation in the local database.
        self.__db = MCT_Database_SQLAlchemy(self.__cfg['database']);

        ##
        try:
            ## Check if that will the minimum execution time is avaliable to ac
            ## cept a request.
            self.__awareMinTime=self.__cfg['main']['global_fairness_req_minimum_time'];

            ## Get time running threshold:
            self.__timeThreshold = int(self.__cfg['main']['min_req_run_threshold']);
        except:
            ## LOG:
            print 'IT IS NOT POSSIBLE FOUND SOME CONFIGS';
            sys.exit(-1);


    ###########################################################################
    ## PUBLIC                                                                ##
    ###########################################################################
    ##
    ## BRIEF: stiop the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def execute(self, playerName):
        fairness = self.__calculate_fairn(playerName);
        print fairness;
        return 0;


    ###########################################################################
    ## PRIVATE                                                               ##
    ###########################################################################
    def __calculate_fairn(self, name):
        accepts  = 0;
        rejects  = 0;
        requests = 0;
        fairness = 0.0;

        ## Obtain all entries from VM table:
        fColumn = (Vm.origin_name == name);

        dRecv = self.__db.all_regs_filter(Vm, fColumn);

        if dRecv != []:
            requests = len(dRecv);

            for request in dRecv:
                status = int(request['status']);
               
                ## Running:
                if   status == 1:
                    accepts += 1;

                elif status == 3:
                    if self.__awareMinTime == "True":
                        tsIni = request['timestamp_received'];
                        tsEnd = request['timestamp_finished'];

                        ## Calculate the time of the instance is running. Accept
                        ## the instance only the time is under the threadshold.
                        tRunSecs = calculate_time(tsIni, tsEnd);

                        if tRunSecs > self.__timeThreshold or tRunSecs < 0.0:
                            accepts += 1;
                        else:
                            rejects += 1;
                    else:
                        accepts += 1;

                else:
                    rejects += 1;

        ## Calculate:
        try:
            fairness = float(accepts) / float(requests);
        except:
            fairness = 0.0;

        return fairness;


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
        main.execute('playerVirtual7');

    except ValueError as exceptionNotice:
        print exceptionNotice;

    except KeyboardInterrupt:
        main.stop();
        print "BYE!";

    sys.exit(0);
## EOF.

