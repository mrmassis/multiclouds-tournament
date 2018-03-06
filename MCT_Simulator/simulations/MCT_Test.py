#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
import time;
import ast;
import sys;
import os;
import operator;
import mysql.connector;
import mysql;
import random;

from mysql.connector import RefreshOption, errorcode;
from multiprocessing import Process, Queue, Lock;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
V_BASE = '/etc/mct/vplayers';
R_BASE = '/etc/mct/quotas'  ;

D_HOST = "localhost";
D_USER = 'mct';
D_PASS = 'password';
D_BASE = 'mct';

COALITION    = 3;
WHITEWASHING = 2; 





###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Test(Process):

    """
    CLASS: execute a set of test situations (by players).
    ---------------------------------------------------------------------------
    ** run - execute in thread.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __mHandleConditions = None;
    __operators         = None;
    __db                = None;
    __testString        = None;
    __vplayerIdsList    = [];
    __coalition         = None;
    __extra             = None;
    __sponsorship       = 0;
    __supporter         = [];


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, testString):
        super(MCT_Test, self).__init__();

        self.__operators = ['==', '>', '<', '!=', '>=', '<='];

        self.__mHandleConditions= {
            'DIVISION': self.__get_division,
            'SCORE'   : self.__get_score,
            'HISTORY' : self.__get_history,
            'ACCEPTS' : self.__get_accepts,
            'REJECTS' : self.__get_rejects,
            'RUNNING' : self.__get_running,
            'FINISHED': self.__get_finished,
            'NOTHING' : self.__nothing
        };

        ## String with test:
        self.__testString = testString;

        ## Database connection:
        dbConfig = {
            'host'             : D_HOST,
            'user'             : D_USER,
            'password'         : D_PASS,
            'database'         : D_BASE,
            'raise_on_warnings': True
        };

        self.__db = mysql.connector.connect(**dbConfig);
        self.__db.autocommit = True;

        ## Work in everiment aware mode (default):
        self.__strategy  = '0';


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: execute thread.
    ## ------------------------------------------------------------------------
    ##
    def run(self): 
        valRet = 0;

        ## Split the string in four others: vplayer, condition, action, and re-
        ## sources.
        pars = self.__testString.split('-');
        
        ## Format and handle each terms presents in parameter list (parameter).
        vplayer, loop, strategy, condition, action, resources = self.__formatParameter(pars);

        ## Get Ids:
        vplayerNm = self.__get_vplayers_ids(vplayer);

        ## Case the strategy is coalition:
        strategy = strategy.split(':');

        if int(strategy[0]) == COALITION:
            self.__strategy = strategy[0];
            self.__extra    = int(strategy[1]);
            self.__increment= int(strategy[1]);
        else:
            self.__strategy = strategy[0];
            self.__increment= 1;

        ## Check if the condtions is valid and return in the dictionary format.
        dictTest = self.__valid_conditions(condition); 

        ## Information abou loop:
        iteractions, timeToWait = loop.split(':');

        i = 0;
        while True:
            time.sleep(float(timeToWait));

            i += self.__increment;

            if dictTest['condition'] == 'TIMER_AFTER':
                functions[action](vplayerNm, action);
            else:
                while True:
                    n=self.__mHandleConditions[dictTest['condition']](vplayerNm);

                    ## Create the conditional to evaluate the trigger.
                    if self.__ops(dictTest['tag'])(n, dictTest['quantity']):
                        if   action == 'UPD':
                            valRet = self.__upd_player(vplayerNm, resources);
                        elif action == 'ADD':
                            valRet = self.__add_player(vplayerNm, resources);
                        elif action == 'DEL':
                            valRet = self.__del_player(vplayerNm);

                        if valRet == 1:
                            return 0;
                        break;

                    time.sleep(5);

            ## Control de iteraction (loop while):
            if i == int(iteractions):
                break;
        return valRet;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: get vplayers ID.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ## 
    def __get_vplayers_ids(self, vplayer):

        prefix, sufix = vplayer.split('_');

        ## One player only:
        if   ',' not in sufix and ':' not in sufix:
            self.__vplayerIdsList.append(sufix);

        ## Set a lot of player defined by alternate id.
        elif ',' in sufix:
            self.__vplayerIdsList = sufix.split(',');

        ## Set a lot of player defined in an interval.
        elif ':' in sufix:
            ini, end = sufix.split(':');

            for idPlayer in range(int(ini), int(end)+1):
                self.__vplayerIdsList.append(idPlayer);

        return prefix;


    ##
    ## BRIEF: update the resources of an existent virtual player.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ## @PARAM resources == list with virtual player resources.
    ##
    def __upd_player(self, vplayer, resources):
        fileNameRT = os.path.join(R_BASE, 'resources'+vplayer[-1] +'.yml');

        ## Create a new resources file with update values.
        templateR = self.__template_resource(vplayer, resources);

        fd = open(fileNameRT, 'w');
        fd.writelines(templateR);
        fd.close();

        return 0;


    ##
    ## BRIEF: add a new virtual player to tournament.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayerNm == virtual player name.
    ## @PARAM resources == list with virtual player resources.
    ##
    def __add_player(self, vplayerNm, resources):

        ## The self.__extra determined the number of the virtual player inser-
        ## ted on same time.
        if self.__extra:
            loop = self.__extra;
        else:
            loop = 1;

        ## Construct the coalition if the vplayer strategy is Free-Riders in a
        ## coalition mode.
        if int(self.__strategy) == COALITION:
            string = '';
            for idx in range(0, self.__extra):
                string += vplayerNm + str(self.__vplayerIdsList[idx]) + ',';

            self.__coalition = string[:-1];

        ##
        for I in range(0, loop):
            try:
                playerId = str(self.__vplayerIdsList[0]);
            except:
                 return 1;

            fileNameVT = os.path.join(V_BASE, 'vplayer'   + playerId + '.yml');
            fileNameRT = os.path.join(R_BASE, 'resources' + playerId + '.yml');

            ## Get the resources and virtual player perfil. Booth are necessry
            ## to add a new player.
            templateR = self.__template_resource(vplayerNm, resources);
            templateV = self.__template_v_player(vplayerNm, playerId );

            fd = open(fileNameRT, 'w'); 
            fd.writelines(templateR);
            fd.close();

            fd = open(fileNameVT, 'w'); 
            fd.writelines(templateV);
            fd.close();

            del self.__vplayerIdsList[0];

            if len(self.__vplayerIdsList) == 0:
                return 1;

        return 0;


    ##
    ## BRIEF: delete existent virtual player.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ##
    def __del_player(self, vplayer):
        fileNameVT = os.path.join(V_BASE, 'vplayer'  +vplayer[-1] +'.yml');
        fileNameRT = os.path.join(R_BASE, 'resources'+vplayer[-1] +'.yml');

        try:
            os.remove(fileNameVT);
            os.remove(fileNameRT);

        except OSError as error:
            print error;
         
        return 0;


    ##
    ## BRIEF: obtain the player's division.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ##
    def __get_division(self, vplayer):
        division = 0;
        query    = 'select division from PLAYER where name="' + vplayer + '"';

        dRecv=self.__select_query(query);

        if dRecv != []:
            for entry in dRecv:
                division = entry[0];

        return division;


    ##
    ## BRIEF: obtain the player's score.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ##
    def __get_score(self, vplayer):
        score    = 0;
        query    = 'select score from PLAYER where name="' + vplayer + '"';

        dRecv = self.__select_query(query);

        if dRecv != []:
            for entry in dRecv:
                score = entry[0];

        return score;


    ##
    ## BRIEF: obtain the player's history.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ##
    def __get_history(self, vplayer):
        history  = 0;
        query    = 'select history from PLAYER where name="' + vplayer + '"';

        dRecv = self.__select_query(query);

        if dRecv != []:
            for entry in dRecv:
                history = entry[0];

        return history;


    ##
    ## BRIEF: obtain the player's accepts vms.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ##
    def __get_accepts(self, vplayer):
        accepts  = 0;
        query    = 'select accepts from PLAYER where name="' + vplayer + '"';

        dRecv = self.__select_query(query);

        if dRecv != []:
            for entry in dRecv:
                accepts = entry[0];

        return accepts;


    ##
    ## BRIEF: obtain the player's reject vms.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ##
    def __get_rejects(self, vplayer):
        rejects  = 0;
        query    = 'select rejects from PLAYER where name="' + vplayer + '"';

        dRecv = self.__select_query(query);

        if dRecv != []:
            for entry in dRecv:
                rejects = entry[0];

        return rejects;


    ##
    ## BRIEF: obtain the player's running vms.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ##
    def __get_running(self, vplayer):
        running  = 0;
        query    = 'select running from PLAYER where name="' + vplayer + '"';

        dRecv = self.__select_query(query);

        if dRecv != []:
            for entry in dRecv:
                running = entry[0];

        return running;


    ##
    ## BRIEF: do nothing.
    ## ------------------------------------------------------------------------
    ##
    def __nothing(self, vplayer):
        return 1;


    ##
    ## BRIEF: obtain the player's finished vms.
    ## ------------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ##
    def __get_finished(self, vplayer):
        finished = 0;
        query    = 'select finished from PLAYER where name="' + vplayer + '"';

        dRecv = self.__select_query(query);

        if dRecv != []:
            for entry in dRecv:
                print entry;

        return finished;


    ##
    ## BRIEF: handle the conditio string. Split in three components.
    ## ------------------------------------------------------------------------
    ## @PARAM conditionString == condition field (unique string).
    ##  
    def __valid_conditions(self, conditionString):

        condition = '';
        quantity  = '';

        for tag in self.__operators:
            if tag in conditionString:
                condition, quantity = conditionString.split(tag);
                break;
        
        dictReturn = {
            'condition': condition,
            'tag'      : tag,
            'quantity' : int(quantity)
        }

        return dictReturn;


    ##
    ## BRIEF: convert operator definied in string to operator mode.
    ## ------------------------------------------------------------------------
    ## @PARAM op == operator (string).
    ##
    def __ops(self, op):

        return {
            '<'  : operator.lt,
            '<=' : operator.le,
            '==' : operator.eq,
            '!=' : operator.ne,
            '>=' : operator.ge,
            '>'  : operator.gt
        }[op];


    ##
    ## BRIEF: create a new vplayer perfil.
    ## -----------------------------------------------------------------------
    ## @PARAM vplayer == virtual player name.
    ##
    def __template_v_player(self, vplayer, playerId): 

        t = [];
        t.append("name                        : " + vplayer + playerId+ "\n");
        t.append("id                          : " + playerId+ "\n");
        t.append("agent_id                    : agent_drive" + playerId + "\n");
        t.append("ratio                       : 610\n");
        t.append("request_pending_iteract     : 10\n");
        t.append("request_pending_waiting     : 60\n");
        t.append("authenticate_address        : 192.168.0.201\n");
        t.append("authenticate_port           : 2000\n");
        t.append("agent_address               : 192.168.0.200\n");
        t.append("resources_file              : /etc/mct/quotas/resources"+playerId+".yml\n");
        t.append("port                        : 10000\n");
        t.append("addr                        : localhost\n");
        t.append("get_set_resources_info_time : 120\n");
        t.append("print                       : logger\n");
        t.append("enable                      : 1\n");

        return t;


    ##
    ## BRIEF: create|modify the virtual player resources.
    ## -----------------------------------------------------------------------
    ## @PARAM vplayer   == virtual player name.
    ## @PARAM resources == virtual player resources.
    ##
    def __template_resource(self, vplayer, resources): 
        
        t = [];
        t.append("vcpus       : " + resources['vcpu']        + "\n");
        t.append("memory      : " + resources['memory']      + "\n");
        t.append("local_gb    : " + resources['local_gb']    + "\n");
        t.append("max_instance: " + resources['max_instance']+ "\n");
        t.append("strategy    : " + self.__strategy          + "\n");

        ## Whitewashing strategu from Free-Riders:
        if int(self.__strategy) == WHITEWASHING:
            t.append("self-sponsorship: " + self.__sponsorship + "\n");
            t.append("supporter       : " + self.__supporter   + "\n");
        else:
            t.append("self-sponsorship: \n");
            t.append("supporter       : \n");

        ## Coalition strategy from Free-Riders.
        if int(self.__strategy) == COALITION:
            t.append("coalition   : " + self.__coalition);
        else:
            t.append("coalition   : ");

        return t;


    ##
    ## BRIEF format and each present in parameter list.
    ## -----------------------------------------------------------------------
    ## @PARAM parameter == parameter list (strings).
    ##
    def __formatParameter(self, parameter):

        vplayer   = parameter[0];
        iteraction= parameter[1];
        strategy  = parameter[2];
        condition = parameter[3];
        action    = parameter[4];
        resources = {};

        if len(parameter) == 6:
            stringResources = parameter[5].split('_');

            ## Check:
            qtde, mod = stringResources[3].split('|');

            ##
            if qtde == '*':
               stringResources[3] = random.randrange(0, int(mod));
            else:
               stringResources[3] = qtde;

            resources['vcpu'        ] = str(stringResources[0]);
            resources['memory'      ] = str(stringResources[1]);
            resources['local_gb'    ] = str(stringResources[2]);
            resources['max_instance'] = str(stringResources[3]);

        return vplayer, iteraction, strategy, condition, action, resources;


    ##
    ## BRIEF: performe a select in the database.
    ## -----------------------------------------------------------------------
    ## @PARAM query == the request.
    ## 
    def __select_query(self, query):
        entry = [];

        try:
            cursor = self.__db.cursor();
            cursor.execute(query);
            for row in cursor:
                entry.append(row);

            cursor.close();

        except mysql.connector.Error as err:
            print(err);

        return entry;

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
    __mapList   = None;
    __fileName  = None;
    __tests     = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM fileName == file name with test.
    ##
    def __init__(self, fileName):

        ## Filename with map test.
        self.__fileName = fileName;

        ## Get the configurantion parameters.
        self.__mapList = self.__get_map_test();


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: start the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def start(self):
        self.__tests = {};

        for action in self.__mapList:
            self.__tests[action] = MCT_Test(action);
            self.__tests[action].daemon = True;
            self.__tests[action].start();

        ## Check if all tests is alive:
        for test in self.__tests:
            self.__tests[test].join();

        return 0;


    ##
    ## BRIEF: stiop the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):

        for test in self.__tests:
            self.__tests[test].terminate();
            self.__tests[test].join();

        return 0;


    ###########################################################################
    ## PRIVATE                                                               ##
    ###########################################################################
    ##
    ## BRIEF: get map test and put in list.
    ## ------------------------------------------------------------------------
    ##
    def __get_map_test(self):
        mapList = [];

        try:
            with open(self.__fileName) as fd:
                content = fd.readlines();
 
            for line in content:
                if line[0] != '#' and len(line) > 2:
                    mapList.append(line.rstrip('\n'));

        except IOError as error:
            print error; 

        return mapList;
## END CLASS.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    try:
        main = Main(sys.argv[1]);
        main.start();

    except ValueError as exceptionNotice:
        print exceptionNotice;

    except KeyboardInterrupt:
        main.stop();
        print "BYE!";

    sys.exit(0);
## EOF.
