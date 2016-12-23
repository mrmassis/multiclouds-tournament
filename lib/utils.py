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
FLV_NAME = {'T':'m1.tiny', 'S':'m1.small', 'B':'m1.medium'};
CPU_INFO = {'T':'1'  , 'S':'1'   , 'B':'2'   };
MEM_INFO = {'T':'512', 'S':'2048', 'B':'4096'};
DSK_INFO = {'T':'1'  , 'S':'20'  , 'B':'40'  };






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

    config = ConfigParser.ConfigParser();
    config.readfp(open(configName));

    ## Scan the configuration file and get the relevant informations and save
    ## then in cfg dictionary.
    for section in config.sections():
        cfg[section] = {};

        for option in config.options(section):
            cfg[section][option] = config.get(section,option);

    return cfg;




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

## EOF.
