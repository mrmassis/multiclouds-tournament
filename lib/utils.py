#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
import ConfigParser;
import inspect;
import random;
import time;





###############################################################################
## DEFINITION                                                                ##
###############################################################################
## Value defined to status when dont find some fields.
MESSAGE_PARSE_ERROR = -10;

## Invalid division:
DIVISION_INVALID = -1;

## Operation code:
GETINF_RESOURCE = 0
SETINF_RESOURCE = 8
CREATE_INSTANCE = 1
DELETE_INSTANCE = 2
SUSPND_INSTANCE = 3
RESUME_INSTANCE = 4
RESETT_INSTANCE = 5
GETINF_INSTANCE = 9

## Instances definitions (SIMULATION):
IMG_NAME = 'cirros-0.3.2-x86_64';
NET_NAME = 'demo-net';

## Information about the flavors. Get from openstack flavors!
FLV_NAME = {'T':'m1.tiny', 'S':'m1.small', 'B':'m1.medium'};
CPU_INFO = {'T':'1'  , 'S':'1'   , 'B':'2'   };
MEM_INFO = {'T':'512', 'S':'2048', 'B':'4096'};
DSK_INFO = {'T':'1'  , 'S':'20'  , 'B':'40'  };

## Dictionary with the convertion of return signal.
GENERIC_STATUS = {
    CREATE_INSTANCE : { 'NOSTATE':0, 'ERROR':0, 'ACTIVE':1},
    DELETE_INSTANCE : { 'NOSTATE':0, 'ERROR':0, 'HARD_DELETED':1,'DELETED':1},
    SUSPND_INSTANCE : { 'NOSTATE':0, 'ERROR':0, 'SUSPENDED'   :1},
    RESUME_INSTANCE : { 'NOSTATE':0, 'ERROR':0, 'ACTIVE'      :1}
}





###############################################################################
## PROCEDURES                                                                ##
###############################################################################
##
## BRIEF: get config options.
## ----------------------------------------------------------------------------
## @PARAM str configName == file with configuration.
##
def get_configs(configName):
    cfg = {};

    try:
        config = ConfigParser.ConfigParser();
        config.readfp(open(configName));

        ## Scan the configuration file and get the relevant infos. Save infos
        ## in a dictionary.
        for section in config.sections():
            cfg[section] = {};

            for option in config.options(section):
                cfg[section][option] = config.get(section,option);

        return cfg;

    except ConfigParser.Error as cfgError:
        raise cfgError;

    return {};




##
## BRIEF: get the caller class.
## ----------------------------------------------------------------------------
## @PARAM deep == deep from get information.
##
def get_class_name_from_frame(deep=0):
    stack = inspect.stack();

    frame = stack[deep][0];
    args, _, _, value_dict = inspect.getargvalues(frame);

    string = value_dict['__file__'];

    ## Extract the information from the name of file.
    string = string.replace('./' ,'');
    string = string.replace('.py','');

    return string;


##
## BRIEF: waiting for a time select from a interval.
## ----------------------------------------------------------------------------
## @PARAM ini == start the interval to select. 
## @PARAM end == finish the interval.
##
def mutable_time_to_waiting(ini, end):

    value = random.uniform(ini, end)
    time.sleep(value);




###############################################################################
## CLASSES                                                                   ##
###############################################################################
class Show_Actions:

    """
    Show_Actions: class that print the received message in the screen or log.
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __choice = None;
    __logger = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, choice, logger=None):

        ## Choice the method to print the message.
        self.__choice = choice;

        ## Assing the logger object to the local attribute. It enable choice to
        ## where the messagem will be printed.
        self.__logger = logger;


    ###########################################################################
    ## PUBLIC METHOS                                                         ##
    ###########################################################################
    ##
    ## BRIEF: show to screen or log the message.
    ## ------------------------------------------------------------------------
    ## @PARAM str msg      == message to show (screen or logger).
    ## @PARAM str severity == message severity.
    ##
    def show(self, message, severity):

        if   self.__choice == 'screen':
            self.__showScreen(message, severity);

        elif self.__choice == 'logger':
            self.__showLogger(message, severity);

        else:
            self.__showBothSL(message, severity);



    ###########################################################################
    ## PRIVATE                                                              ##
    ###########################################################################
    ##
    ## BRIEF: show message on the screen and logger.
    ## ------------------------------------------------------------------------
    ## @PARAM str msg      == message to show (screen or logger).
    ## @PARAM str severity == message severity.
    ##
    def __showBothSL(self, message, severity):
        self.__showScreen(message, severity);
        self.__showLogger(message, severity);


    ##
    ## BRIEF: show message on the screen.
    ## ------------------------------------------------------------------------
    ## @PARAM str msg      == message to show (screen or logger).
    ## @PARAM str severity == message severity.
    ##
    def __showScreen(self, message, severity):
        print '[' + severity + '] ' + message;


    ##
    ## BRIEF: show message in the logger.
    ## ------------------------------------------------------------------------
    ## @PARAM str msg      == message to show (screen or logger).
    ## @PARAM str severity == message severity.
    ##
    def __showLogger(self, message, severity):

        if   severity == 'I':
            self.__logger.info(message);

        elif severity == 'E':
            self.__logger.error(message);
## EOF.
