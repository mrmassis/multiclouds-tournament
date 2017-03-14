#!/usr/bin/env python


import sys;
import json;
import time;
import logging;
import logging.handlers;
import pika;
import datetime;

from mct.lib.utils     import *;
from mct.lib.openstack import MCT_Openstack_Nova;
from mct.lib.amqp      import RabbitMQ_Publish;









###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE  = '/etc/mct/mct-quotas.ini';
LOG_NAME     = 'MCT_Quotas';
LOG_FORMAT   = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME = '/var/log/mct/mct_quotas.log';
DISPATCH_NAME= 'MCT_Dispatch';








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
class MCT_Quotas:

    """
    Class MCT_Quotat. 
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __route         = None;
    __publish       = None;
    __addrExternal  = None;
    __cloud         = None;
    __timeToPublish = None;
    __print         = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        config = get_configs(CONFIG_FILE);

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(config['main']['print'], logger);

        ## Local address and name:
        self.__playerAddr = config['properties']['addr'];
        self.__playerName = config['properties']['name'];

        ## Time to publish the message to dispatch. The time is in "seconds".
        self.__timeToPublish = config['main']['time_to_publish'];

        ## Get which route is used to deliver the msg to the 'correct destine'.
        self.__route = config['amqp_external_publish']['route'];

        ### Credentials:
        config['amqp_external_publish']['user'] = config['rabbitmq']['user'];
        config['amqp_external_publish']['pass'] = config['rabbitmq']['pass'];

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish = RabbitMQ_Publish(config['amqp_external_publish']);

        ## Check the type of framework utilized to build the cloud.Intance the
        ## correct API.
        if config['cloud_framework']['type'] == 'openstack':
            self.__cloud = MCT_Openstack_Nova(config['cloud_framework']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: publish the quota avaliable to MCT.
    ## ------------------------------------------------------------------------
    ##
    def publish_quota(self):

        ## Build the message:
        message = {
            'code'    : SETINF_RESOURCE,
            'playerId': self.__playerName,
            'status'  : 0,
            'reqId'   : '',
            'retId'   : '',
            'origAddr': self.__playerAddr,
            'destAddr': '',
            'destName': '',
            'data'    : ''
        }

        while True:
            ## Get the resources avaliable to 'MCT' from the 'framework' object.
            quota = self.__get_quota();

            data = {
                'vcpus' : quota['vcpus' ],
                'memory': quota['memory'],
                'disk'  : quota['disk'  ]
            }

            message['data'] = data;

            ## Send the message with quota to dispatch. Update the base of re-
            ## sources.
            self.__send_message_dispatch(message, 'MCT_Quota'); 

            time.sleep(float(self.__timeToPublish));

        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: get quota from framework.
    ## ------------------------------------------------------------------------
    ##
    def __get_quota(self):

        ## To each framework suported use a method to get the total quota:
        quota = self.__cloud.get_quota();
        
        if quota == {}:
            quota = {
                'vcpus' : 0,
                'memory': 0,
                'disk'  : 0
            };
      
        return quota;


    ##
    ## BRIEF: send message to MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __send_message_dispatch(self, message, appId):

        ## Publish the message to MCT_Dispatch via AMQP. The MCT_Dispatch is in
        ## the remote server. 
        valRet = self.__publish.publish(message, self.__route);

        if valRet == False:
            ## LOG:
            logger.error("IT WAS NOT POSSIBLE TO SEND THE MSG TO DISPATCH!");
        else:
            ## LOG:
            logger.info ('MESSAGE SENT TO DISPATCH!');

        return 0;
## END.







###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    try:
        mct = MCT_Quotas();
        mct.publish_quota();

    except KeyboardInterrupt:
        pass;

    sys.exit(0);
## EOF
