#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
import time;
import ast;
import sys;
import os;
import operator;

from multiprocessing import Process, Queue, Lock;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
V_BASE = '.';
R_BASE = '.';








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Test(Process):

    """
    CLASS:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __mHandleConditions = None;
    __operators         = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, testString):
        super(MCT_Test, self).__init__();

        ##
        self.__operators = ['==', '>', '<', '!=', '>=', '<='];

        ##
        self.__mHandleConditions= {
            'DIVISION': self.__get_division,
            'SCORE'   : self.__get_score,
            'HISTORY' : self.__get_history,
            'ACCEPTS' : self.__get_accepts,
            'REJECTS' : self.__get_rejects,
            'RUNNING' : self.__get_running,
            'FINISHED': self.__get_finished
        };

        ## String with test:
        self.__testString = testString;


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: execute thread.
    ## ------------------------------------------------------------------------
    ##
    def run(self): 
        ## Split the string in four others: vplayer, condition, action, and re-
        ## sources.
        parameters = self.__testString.split('-');
        
        ## Format and handle each terms presents in parameter list (parameter).
        vplayer,condition,action,resources =self.__formatParameter(parameters);

        ## Check if the condtions is valid and return in the dictionary format.
        dictTest = self.__valid_conditions(condition); 

        if dictTest['condition'] == 'TIMER_AFTER':
            functions[action](vplayer, action);

        else:
            while True:
                n = self.__mHandleConditions[dictTest['condition']](vplayer);

                ## Create (on-demand) the conditional to evaluate the trigger.
                if self.__ops(dictTest['tag'])(n, dictTest['quantity']):

                    if   action == 'UPD':
                       self.__upd_player(vplayer, resources);

                    elif action == 'ADD':
                       self.__add_player(vplayer, resources);

                    elif action == 'DEL':
                       self.__del_player(vplayer);

                    break;

                time.sleep(5);
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
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
    ## @PARAM vplayer == virtual player name.
    ## @PARAM resources == list with virtual player resources.
    ##
    def __add_player(self, vplayer, resources):

        fileNameVT = os.path.join(V_BASE, 'vplayer'  +vplayer[-1] +'.yml');
        fileNameRT = os.path.join(R_BASE, 'resources'+vplayer[-1] +'.yml');

        ## Get the resources and virtual player perfil. Booth are necessry to 
        ## add a new player.
        templateR = self.__template_resource(vplayer, resources);
        templateV = self.__template_v_player(vplayer);

        fd = open(fileNameRT, 'w'); 
        fd.writelines(templateR);
        fd.close();

        fd = open(fileNameVT, 'w'); 
        fd.writelines(templateV);
        fd.close();

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
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def __get_division(self, vplayer):
        return 0;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def __get_division(self, vplayer):
        return 0;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def __get_score(self, vplayer):
        return 0;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def __get_history(self, vplayer):
        return 0;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def __get_accepts(self, vplayer):
        return 10;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def __get_rejects(self, vplayer):
        return 0;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def __get_running(self, vplayer):
        return 0;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def __get_finished(self, vplayer):
        return 0;


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
    def __template_v_player(self, vplayer): 

        numberId = "agent_drive" + vplayer[-1];

        t = [];
        t.append("name                        : " + vplayer + "\n");
        t.append("amqp_identifier             : " + vplayer + "\n");
        t.append("amqp_address                : localhost\n");
        t.append("amqp_route                  : mct_agent\n");
        t.append("amqp_exchange               : mct_exchange\n");
        t.append("amqp_queue_name             : agent\n");
        t.append("amqp_user                   : mct\n");
        t.append("amqp_pass                   : password\n");
        t.append("agent_id                    : " + numberId + "\n");
        t.append("ratio                       : 610\n");
        t.append("request_pending_iteract     : 10\n");
        t.append("request_pending_waiting     : 60\n");
        t.append("authenticate_address        : 192.168.0.201\n");
        t.append("authenticate_port           : 2000\n");
        t.append("agent_address               : 192.168.0.200\n");
        t.append("resources_file              : /etc/mct/quotas/resources.yml\n");
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
        t.append("name: "         + vplayer                  + "\n");
        t.append("vcpus: "        + resources['vcpu']        + "\n");
        t.append("memory: "       + resources['memory']      + "\n");
        t.append("local_gb: "     + resources['local_gb']    + "\n");
        t.append("max_instance: " + resources['max_instance']+ "\n");

        return t;


    ##
    ## BRIEF format and each present in parameter list.
    ## -----------------------------------------------------------------------
    ## @PARAM parameter == parameter list (strings).
    ##
    def __formatParameter(self, parameter):

        vplayer   = parameter[0];
        condition = parameter[1];
        action    = parameter[2];
        resources = {};

        if len(parameter) == 4:
            stringResources = parameter[3].split('_');

            resources['vcpu'        ] = stringResources[0];
            resources['memory'      ] = stringResources[1];
            resources['local_gb'    ] = stringResources[2];
            resources['max_instance'] = stringResources[3];

        return vplayer, condition, action, resources;
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
