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
class Manager(Process):

    """
    Class Manager:
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    * run == .
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __maxDivision    = None;
    __queue          = None;
    __db             = None;
    __print          = None;
    __distribute     = None;
    __distributeMode = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, dictCfg):
        super(Manager, self).__init__();

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(dictCfg['cfg']['print'],dictCfg['logger']);

        ## LOG:
        self.__print.show('INITIALIZE MANAGER PROCESS', 'I');

        ## Obtain the max division from tournament:
        self.__maxDivision = dictCfg['maxDivision'];

        ## Check if distribute is enable:
        self.__distribute = dictCfg['distribute'];

        if self.__distribute == 'True':
            self.__distributeMode = dictCfg['distribute_mode'];

        ## Get the queues:
        self.__queue = dictCfg['queue'];

        ## Dtabase object:
        self.__db = dictCfg['db'];


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## Brief: threshold main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        while True:
            ## Get a request from threads:
            player = self.__queue.get();

            ## Store the value:
            valRet = self.__do_action(player);

        return SUCCESS;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: execute an action.
    ## ------------------------------------------------------------------------
    ## @PARAM player == player information. 
    ##
    def __do_action(self, player):
        
        ## Check if the distribute mode is enable:
        if self.__distribute == 'True':
            if self.__distributeMode == 'Pyramid':
                valRet, player = self.__distribute_players(player);
        else:
            valRet = SUCCESS;

        if valRet == SUCCESS:

            ## Delete old division key;
            try:
                del player['old'];
            except KeyError:
                pass;

            ## :::
            fColumns = (Player.name == player['name']);

            with self.__db['lock']:
                self.__db['db'].update_reg(Player, fColumns, player);

        return valRet;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM player == player information. 
    ##
    def __distribute_players(self, player):
        ## Size:
        divisionsSize = [0] * self.__maxDivision;

        for idx in range(1, self.__maxDivision + 1):
            ## Filter by column. Select all player that belong to the specific
            ## divisio:
            fColumns = (Player.division == idx);

            with self.__db['lock']:
                 dRecv = self.__db['db'].all_regs_filter(Player, fColumns);

            divisionsSize[idx-1] = len(dRecv);

        tDiv = int(player['division']);
        fDiv = int(player['old'     ]);

        ## Check if is to upgrade or downgrade player:
        result = tDiv - fDiv;

        if tDiv != 4 and fDiv != 4:
            ## Upgrade:
            if result < 0:
                ## Apply the algorithm:
                if divisionsSize[tDiv-1] + 1 >= divisionsSize[fDiv-1]: 
                    return FAILED, player;
            ## Down:
            elif result > 0:
                ## Apply the algorithm:
                if divisionsSize[tDiv-1] + 1 >= divisionsSize[fDiv-1]: 
                    ## Setting "tapetao":
                    player['cushion'] = 1;

                    return FAILED, player;
                else:
                    ## Check if the division is empty. If yes setting state to.
                    ## wo state.
                    pass;

            player['cushion'] = 0;

        return SUCCESS, player;
## END OF CLASS.








class Threshold_Monitor(Process):

    """
    Class Threshold_Monitor:
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    * run == threshold main loop.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __print          = None;
    __db             = None;
    __approach       = None;
    __interval       = None;
    __numberDivisions= None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, cfg, db, logger, divisions):
        super(Threshold_Monitor, self).__init__();

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['print'], logger);

        ## LOG:
        self.__print.show('INITIALIZE THRESHOLD MONITOR', 'I');

        ## Get the threshold approach:
        self.__approach = cfg['approach'];

        ## Get loop waiting interval. This value determine the time to waiting
        ## between the loops.
        self.__interval = float(cfg['interval']);

        ## Obtain total of divisions:
        self.__numberDivisions = divisions;

        ## Setting the database attribute. In this attribute are the db connec-
        ## tion and the lock to avoid data corruption.
        self.__db = db;

        ## Setting the initial values to threshold table:
        self.__set_initial_values(cfg['min_values'], cfg['max_values']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## Brief: threshold main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        while True:

            ## Use the static approach to setting the threshold:
            if self.__approach == 'static':  
                self.__static();

            time.sleep(self.__interval);

        return SUCCESS;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: in static mode 
    ## ------------------------------------------------------------------------
    ##
    def __static(self):
        return SUCCESS;


    ##
    ## BRIEF: set the initial values to threshold table.
    ## ------------------------------------------------------------------------
    ## @PARAM minValues == list of botton threshold (by division).
    ## @PARAM maxValues == list of top    threshold (by division).
    ##
    def __set_initial_values(self, minValues, maxValues):

        minValues = minValues.split(',');
        maxValues = maxValues.split(',');

        idx = 0;
        for division in reversed(range(1, self.__numberDivisions+1)):
            ## Insert:
            threshold = Threshold();

            threshold.division = division;
            threshold.botton   = float(minValues[idx]);
            threshold.top      = float(maxValues[idx]);
            
            try:
                self.__db['db'].insert_reg(threshold);

            except:
                data = {
                    'botton': float(minValues[idx]),
                    'top'   : float(maxValues[idx])
                };

                fColumn = (Threshold.division == division);

                self.__db['db'].update_reg(Threshold, fColumn, data);

            idx += 1;

        return SUCCESS;
## END CLASS.








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
    __print           = None;
    __db              = None;
    __id              = None;
    __interval        = None;
    __round           = None;
    __awareMinTime    = None;
    __timeThreshold   = None;
    __maxDivision     = None;
    __realloc         = None;
    __attributes      = None;
    __awareMinTime    = None;
    __timeThreshold   = None;
    __queue           = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, dictCfg):
        super(Division, self).__init__();

        cfg = dictCfg['cfg'];

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['print'], dictCfg['logger']);

        ## Get the identification number (id) of division.
        self.__id = cfg['id'];

        ## Get loop waiting interval. This value determine the time to waiting
        ## between the loops.
        self.__interval = float(cfg['loop_interval']);

        ## Get the round value. At end of this value the system compute the pla
        ## eyrs attributes.
        self.__round = float(cfg['round']);

        ## Obtain the max division in tournament:
        self.__maxDivision = dictCfg['maxDivision'];

        ## LOG:
        self.__print.show('INITIALIZE DIVISION: ' + self.__id, 'I');

        ## Setting the database attribute. In this attribute are the db connec-
        ## tion and the lock to avoid data corruption.
        self.__db = dictCfg['db'];

        ## Enable realloc players by divisions:
        self.__realloc = cfg['realloc'];

        ## Setting comunnication channel.
        self.__queue =dictCfg['queue'];

        ## Optional:
        try:
            ## Check if that will the minimum execution time is avaliable to ac
            ## cept a request.
            self.__awareMinTime=cfg['individual_fairness_request_minimum_time'];

            ## Get time running threshold:
            self.__timeThreshold = float(cfg['min_instance_run_threshold']);
        except:
            pass;

        ## Attributes.
        self.__attributes =getattr(importlib.import_module(ATTRIBUTES_MODULE),
                                                              'MCT_Attributes');


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
            
            ## Minutes:
            if float(divmod(eT.total_seconds(),60)[0]) >= self.__round:
                 ## LOG:
                 self.__print.show('\n-------------------------------', 'I');

                 ## LOG:
                 self.__print.show('ROUND ENDED DIV: '+str(self.__id), 'I');

                 ## Calculate attributes (score|hist) of each player in the div.
                 self.__end_of_round();

                 ## LOG:
                 self.__print.show('-------------------------------\n', 'I');

                 timeOld = datetime.datetime.now();

            time.sleep(self.__interval);

        return SUCCESS;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: Calculate attributes of each player in the  division.
    ## ------------------------------------------------------------------------
    ## 
    def __end_of_round(self):

        ## LOG:
        self.__print.show('CALC PLAYER ATTR FROM DIV: '+str(self.__id),'I');

        ## Select all player belongs at division self.__id (1, 2, 3, 4 ..., n);
        fColumns = (Player.division == self.__id);

        with self.__db['lock']:
            dRecv = self.__db['db'].all_regs_filter(Player, fColumns);

        if dRecv != []:
            ## Obtain division limits.  
            thresholds = self.__obtain_thresholds();

            ## To each player belong to division calculate the attributes (sco-
            ## res, history etc).
            for player in dRecv:

                data = {
                    'name'    : player['name'],
                    'score'   : float(player['score'   ]),
                    'fairness': float(player['fairness']),
                    'history' : int(  player['history' ]),
                    'division': int(  player['division']),
                    'old'     : int(  player['division']),
                    'playoff' : int(  player['playoff' ]),
                    'enabled' : int(  player['enabled' ])
                };

                ## Calculate three player's attributes: new score, new individu
                ## al fairness, and new history.
                data = self.__calculate_score(data);
                data = self.__calculate_fairn(data);
                data = self.__calculate_histc(data, thresholds);
               
                ## LOG:
                self.__print.show('NEW DATA : ' + str(data), 'I');

                if self.__realloc == "True":
                    data = self.__realloc_player_by_divisions(data, thresholds);

                self.__queue.put(data);

        ## LOG:
        self.__print.show('NEWS ATTRS CALCULATED TO DIV: '+str(self.__id),'I');
        return 0;


    ##
    ## BRIEF: obtain the division' thresholds.
    ## ------------------------------------------------------------------------
    ## 
    def __obtain_thresholds(self):

        fColumns = (Threshold.division == self.__id);

        with self.__db['lock']:
            dRecv = self.__db['db'  ].all_regs_filter(Threshold, fColumns);

        bThreshold = float(dRecv[-1]['botton']);
        tThreshold = float(dRecv[-1]['top'   ]);

        return (bThreshold, tThreshold);


    ##
    ## BRIEF: calculate a new player's score. 
    ## ------------------------------------------------------------------------
    ## @PARAM data == player data dictionary.
    ## 
    def __calculate_score(self, data):

        ## Obtain all entry that meaning requests indicated to the player:
        fColumn = (Vm.destiny_name == data['name']);

        with self.__db['lock']:
            dRecv = self.__db['db'].all_regs_filter(Vm, fColumn);

        if dRecv != []:
            data['score'] = self.__attributes.calculate_score(dRecv);

        ## LOG:
        self.__print.show(data['name'] + ' NEW SCORE:'+str(data['score']),'I');

        return data;


    ##
    ## BRIEF: calculate a new player's historic.
    ## ------------------------------------------------------------------------
    ## @PARAM data       == player data dictionary.
    ## @PARAM thresholds == botton and up threshold'division.
    ## 
    def __calculate_histc(self, data, thresholds):
        threshold = thresholds[0]

        ## Obtain the old history:
        history = data['history'];
        score   = data['score'  ];

        ## check playoff state
        if data['playoff'] == PLAYOFF_OUT:
            data['history'] = self.__attributes.calculate_history(score, 
                                                                  history, 
                                                                  threshold);
        ## LOG:
        self.__print.show(data['name']+' NEW HIST:'+str(data['history']),'I');
        return data;


    ##
    ## BRIEF: calculate player fairness.
    ## ------------------------------------------------------------------------
    ## @PARAM data == player data dictionary.
    ## 
    def __calculate_fairn(self, data):
        accepts  = 0;
        rejects  = 0;
        requests = 0;

        ## Obtain all entries from VM table:
        fColumn = (Vm.origin_name == data['name']);

        with self.__db['lock']:
            dRecv = self.__db['db'].all_regs_filter(Vm, fColumn);

        if dRecv != []:
            requests = len(dRecv);

            for request in dRecv:
                status = int(request['status']);

                if   status == 1:
                    accepts += 1;

                elif status == 3 or status == 2:

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
            data['fairness'] = float(accepts) / float(requests);
        except:
            data['fairness'] = 0.0;

        return data;


    ##
    ## BRIEF: realloc the player by divisions.
    ## ------------------------------------------------------------------------
    ## @PARAM player == player data dictionary.
    ## 
    def __realloc_player_by_divisions(self, player, thresholds):
 
        ## LOG:
        self.__print.show('START TH REALLOC PROCESS...', 'I');

        if player['playoff'] == 1:
            player = self.__playoff_mode(player, thresholds);
        else:
            player = self.__normal_mode(player , thresholds);

        return player;


    ##
    ## BRIEF: handle the player in normal mode (playoff == False).
    ## ------------------------------------------------------------------------
    ## @PARAM player     == player data dictionary.
    ## @PARAM thresholds == botton and up threshold'division.
    ##
    def __normal_mode(self, player, thresholds):
        ## LOG:
        self.__print.show('NORMAL MODE...', 'I');

        ## Promote player:
        if   player['score'] >= thresholds[1]:

            ## Check if the division is not the firs, does not exist other divi
            ## sion to reach.
            if player['division'] != 1:
                 player['division'] = player['division'] - 1;

        ## Demote player:
        elif player['score'] < thresholds[0]:
            player['playoff'] = PLAYOFF_IN;

        return player;


    ##
    ## BRIEF: handle the player in normal mode (playoff == True).
    ## ------------------------------------------------------------------------
    ## @PARAM player     == player data dictionary.
    ## @PARAM thresholds == botton and up threshold'division.
    ##
    def __playoff_mode(self, player, thresholds):
        ## LOG:
        self.__print.show('PLAYOFF MODE...', 'I');

        ## Promote player:
        if   player['score'] >= thresholds[1]:
                
            ## Check if the division is not the firs, does not exist other divi
            ## vision to reach.
            if player['division'] != 1:
                player['division'] = player['division'] - 1;

            player['playoff'] = PLAYOFF_OUT;

        ## Demote player:
        elif player['score'] < thresholds[0]:

            ## If the player has history to maintain hinself in the playoff de-
            ## crement the history.
            if player['history'] > 0:
                ## Drecrement the player' history:
                player['history' ] = player['history' ] - 1;
            else:
                ## Demote the player:
                player['division'] = player['division'] + 1;

                ## Check if the player is in access division:
                if player['division'] > self.__maxDivision:
                    player['enabled'] = PLAYER_DISABLED;

        ## Exit from playoff status.
        else:
            player['playoff'] = PLAYOFF_OUT;

        return player;      
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
    __threadsId           = [];
    __db                  = None;
    __logger              = None;
    __divCfgs             = [];
    __print               = None;
    __thresholdCfg        = None;
    __runThresholdMonitor = None;
    __awareMinTime        = None;
    __timeThreshold       = None;
    __queue               = [];
    __cfg                 = None;
    __distribute          = None;
    __distributeMode      = None;


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
        self.__print.show('INITIALIZE ALL DIVISIONS!', 'I');

        ## Get the configurations related to the execution of the divisions de
        ## fined by the User.
        self.__logger = logger;

        ## Set distribute:
        self.__distribute = cfg['main']['distribute'];

        ## Case the distribute is enable obtain the distribute approache that
        ## will be used.
        if self.__distribute == 'True':
            self.__distributeMode = cfg['distribute']['mode'];

        ## Get the number of division setting to tournament.This value will be
        ## used to define max division.
        self.__divisions = int(cfg['main']['divisions']);

        for div in range(1, self.__divisions + 1):
            self.__divCfgs.append(cfg['division' + str(div)]);
        
        ## Create the division's queues to comunicate between divs. and manage.
        self.__queue = Queue();
        
        ## Intance a new object to handler all operation in the local database.
        self.__db = {
            'db'  : MCT_Database_SQLAlchemy(cfg['database']),
            'lock': Lock()
        };

        ## Obtain information about threshold, if True the monitor will be run.
        self.__runThresholdMonitor = cfg['main']['monitor_threshold'];

        ## Threshold monitor configuration.       
        self.__thresholdCfg = cfg['threshold'];

        ## Cfg:
        self.__cfg = cfg['main'];

        try:
            ## Check if that will the minimum execution time is avaliable to ac
            ## cept a request.
            self.__awareMinTime=cfg['main']['global_fairness_req_minimum_time'];

            ## Get time running threshold:
            self.__timeThreshold = int(cfg['main']['min_req_run_threshold']);
        except:
            ## LOG:
            self.__print.show("IT IS NOT POSSIBLE FOUND SOME CONFIGS", 'I');
            sys.exit(-1);
 
        ## Load attribute calculation module:
        global ATTRIBUTES_MODULE;
        ATTRIBUTES_MODULE = cfg['attributes']['calculation_attrs'];


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        ## Create all threads.The number of threads are defineds in the cfgFile.
        for div in range(0, self.__divisions):
            self.start(div);

        ## Run the threshold monitor.
        if self.__runThresholdMonitor == "True":
            self.__run_threshold_monitor();

        ## Run the manager process:
        self.__run_manager();

        self.__waiting_finish();
        return SUCCESS;


    ##
    ## BRIEF: start a thread.
    ## ------------------------------------------------------------------------
    ## @PARAM division == division id.
    ##
    def start(self, division):
        ## LOG:
        self.__print.show('START A NEW DIVISION IN THE MCT', 'I');

        dictCfg = {
            'cfg'        : self.__divCfgs[division],
            'db'         : self.__db,
            'logger'     : self.__logger,
            'maxDivision': self.__divisions,
            'queue'      : self.__queue
        };

        ## Start the new division running in thread.
        newDivision = Division(dictCfg);
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
    ## BRIEF: execute threshold monitor.
    ## ------------------------------------------------------------------------
    ## 
    def __run_threshold_monitor(self):
        ## LOG:
        self.__print.show('START THE THRESHOLD MONITOR', 'I');

        ## Start the new division running in thread.
        threshold = Threshold_Monitor(self.__thresholdCfg, 
                                      self.__db, 
                                      self.__logger, 
                                      self.__divisions);
        threshold.daemon = True;
        threshold.start();

        return SUCCESS;


    ##
    ## BRIEF: execute manager.
    ## ------------------------------------------------------------------------
    ## 
    def __run_manager(self):
        ## LOG:
        self.__print.show('START THE MANAGER PROCESS', 'I');

        dictCfg = {
            'cfg'             : self.__cfg,
            'db'              : self.__db,
            'logger'          : self.__logger,
            'maxDivision'     : self.__divisions,
            'queue'           : self.__queue,
            'distribute'      : self.__distribute,
            'distribute_mode' : self.__distributeMode
        };

        ## Start the new division running in thread.
        manager = Manager(dictCfg);
        manager.daemon = True;
        manager.start();

        return SUCCESS;


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
        with self.__db['lock']:
            dRecv = self.__db['db'].all_regs(Vm);

        if dRecv != []:
            ## Obtain the number of the all request by create new VM instances.
            allReqs = len(dRecv);

            for vm in dRecv:
                ## If the vm is finished or running they were accepts.
                if  int(vm['status']) != FAILED:

                    if self.__awareMinTime == "True":
                        tsIni = vm['timestamp_received'];
                        tsEnd = vm['timestamp_finished'];

                        ## Calculate the time of the instance is running. Accept
                        ## the instance only the time is under the threadshold.
                        tRunSecs = calculate_time(tsIni, tsEnd);

                        if tRunSecs >  self.__timeThreshold or tRunSecs < 0.0:
                            accepts += 1;
                        else:
                            rejects += 1;
                    else:
                        accepts += 1;
                else:
                    rejects += 1;

            ## Calculate:
            try:
                globalFairness = float(accepts) / float(allReqs);
            except:
                globalFairness = 0.0;

        ## Obtain all players in tournament in this momment:
        with self.__db['lock']:
            players = self.__db['db'].all_regs(Player);

        status = Status();

        status.players      = len(players);
        status.all_requests = allReqs;
        status.accepts      = accepts;
        status.rejects      = rejects;
        status.fairness     = globalFairness;
        status.timestamp    = str(datetime.datetime.now());

        with self.__db['lock']:
            self.__db['db'  ].insert_reg(status);
              
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
        self.__cfg = self.__get_configs();

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

