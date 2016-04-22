#!/usr/bin/env python


import pika;
import time;
import sys;
import os;
import datetime;
import ConfigParser;
import json;
import logging;
import logging.handlers;

from multiprocessing  import Process, Queue, Lock;
from lib.scheduller   import Roundrobin;
from lib.amqp         import RabbitMQ_Publish, RabbitMQ_Consume;





###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE   = '/etc/mct/mct_referee.ini';
LOG_NAME      = 'MCT_Referee';
LOG_FORMAT    = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME  = '/var/log/mct/mct_referee.log';








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
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __div        = None;
    __cfg        = None;
    __queue      = None;
    __scheduller = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, division, name, config, amqp, queue):
        super(Division, self).__init__(name=name);

        if config['scheduller'] == 'roundrobin':
            self.__scheduller = Roundrobin(division);

        self.__div   = division;
        self.__cfg   = config;
        self.__queue = queue;

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publisher = RabbitMQ_Publish(amqp);


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
            try:
                message = self.__queue.get(True, 5);
            except:
                message = '';
                pass;

            if message:

                ## LOG:
                logger.info('DIV: %s RECEIVED THE MSG: %s',self.__div,message);

                ## When the div. receiving the message performs all tasks rela-
                ## ted to the action described in the message.
                self.__exec_action(message);

                ## Obtain the current time . The value is used to calculate the
                ## time difference .
                timeNow = datetime.datetime.now();

                ## Elapsed time of the last round until now. Used to check the
                ## next round.
                elapsedTime = timeNow - timeOld;

                if divmod(elapsedTime.total_seconds(), 60)[0] >= 5:
                    #self.__scheduller.run();

                   timeOld = datetime.datetime.now();

        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: execute the appropriate action in response to the request.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == request receveid from MCT_Divisions. 
    ## 
    def __exec_action(self, message):

        response = {
            'action': message['action'],
            'player': message['player'],
            'msg_id': message['msg_id'],
            'status': 'ok'
        }

        self.__publisher.publish(message, 'mct_dispatch');
        
        ## LOG:
        logger.info('RESPONSE SENT: %s', response);
        return 0;
## END.






class MCT_Referee(RabbitMQ_Consume):

    """
    CLASS: start and mantain the MCT referee.
    ---------------------------------------------------------------------------
    run            == create the divisions and wait in loop.
    gracefull_stop == grecefull finish the divisions.

    __get_configs  == get config options.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __threadsId     = None;
    __allQueues     = None;
    __routeDispatch = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        ## Get the configurations related to the execution of the divisions de-
        ## fined by the User.
        configs = self.__get_configs(CONFIG_FILE);

        ## Get which route is used to deliver the message to the MCT_Dispatch.
        self.__routeDispatch = configs['amqp_publish']['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, configs['amqp_consume']);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish=RabbitMQ_Publish(configs['amqp_publish']);

        ## This list store the thread IDs that represet each division started.
        #self.__threadsId = [];

        ## Create a list of Queues to comunicate with divisions run in thread.
        #self.__allQueues = [];

        ## Instance the divisions that will be used in MultiClouds Tournament.
        #for divNumb in range(1, int(cfg['main']['num_divisions']) + 1):
        #     newQueue = Queue();

        #     divName = 'division' + str(divNumb);
        #     divConf = cfg[divName];
        #     divAmqp = cfg['amqp' ];

        #     division = Division(divNumb, divName, divConf, divAmqp, newQueue);
        #     division.daemon = True;
        #     division.start();

        #     self.__threadsId.append(division);
        #     self.__allQueues.append(newQueue);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: grecefull finish the divisions.
    ## ------------------------------------------------------------------------
    ##
    def gracefull_stop(self):
        for thread in self.__threadsId:
            thread.terminate();
            thread.join();

        ## LOG:
        logger.info('GRACEFULL STOP...');
        return 0;


    ##
    ## BRIEF: method invoked when the pika receive a message.
    ## ------------------------------------------------------------------------
    ## @PARAM pika.Channel              channel    = the communication channel.
    ## @PARAM pika.spec.Basic.Deliver   method     = 
    ## @PARAM pika.spec.BasicProperties properties = 
    ## @PARAM str                       message    = message received.
    ##
    def callback(self, channel, method, properties, message):
        ## LOG:
        logger.info('MESSAGE %s RECEIVED FROM: %s.',message,properties.app_id);

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        ## The json.loads translate a string containing JSON data into a Python
        ## value.
        message = json.loads(message);

        ## Check if the message received is valid. Verify all fields in the mes
        ## sage.
        valRet = self.__inspect_request(message);

        ## Check if is a request or a response received from the apropriate pla
        ## yer. When message['retId'] equal a '' the message is a request.
        if message['retId'] == '':

            ## 
            message['retId'] = message['reqId'];
  
            ## TEM QUE CHECAR QUAL A ACAO A SER REALIZADA.
            if int(message['code']) == 1:
                ## Get which division than player belong.It is necessary to get
                ## the player list able to meet the request.
                ## division = self.__get_division(message['playerId']);

                ## Choise the best player ablet to meet the request to instance
                ## creation.
                ## playerChoiseAddress = self.__get_player(division);
                playerChoiseAddress = '20.0.0.30';

                ##
                message['destAdd'] = playerChoiseAddress;
        else:
            message['retId'  ] = '';

        #if properties.app_id == 'MCT_Dispatch' and valRet == 0:
        #    self.__allQueues[divId-1].put(messageDict);
        self.__publish.publish(message, self.__routeDispatch);
        return 0;



    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: check if reques is valid.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __inspect_request(self, request):
        ## LOG:
        logger.info('INSPECT REQUEST!');

        ## Verify other aspect from request.

        #keywords = [
        #    'action',
        #    'player',
        #    'msg_id',
        #    'vmt_id',
        #    'div_id'
        #];

        #for key in keywords:
        #     if not request.has_key(key):
        #        print "LOG: missed field " + key;
        #        return 1;

        return 0;


    ##
    ## BRIEF: get config options.
    ## ------------------------------------------------------------------------
    ## @PARAM str configName == file with configuration.
    ##
    def __get_configs(self, configName):
        cfg = {};

        config = ConfigParser.ConfigParser();
        config.readfp(open(configName));

        ## Scan the configuration file and get the relevant informations and sa
        ## ve then in cfg dictionary.
        for section in config.sections():
            cfg[section] = {};

            for option in config.options(section):
                cfg[section][option] = config.get(section,option);

        return cfg;
## END.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    ## LOG:
    logger.info('EXECUTION STARTED...');

    try:
        mctReferee = MCT_Referee();
        mctReferee.consume();

    except KeyboardInterrupt, error:
        mctReferee.gracefull_stop();

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF.

