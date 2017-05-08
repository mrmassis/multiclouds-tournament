#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
import ConfigParser;





###############################################################################
## DEFINITION                                                                ##
###############################################################################
## Operation code:
GETINF_RESOURCE = 0
CREATE_INSTANCE = 1
DELETE_INSTANCE = 2
SUSPND_INSTANCE = 3
RESUME_INSTANCE = 4
RESETT_INSTANCE = 5
GETINF_INSTANCE = 9




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

## EOF.
