#!/usr/bin/env python


import pika;
import time;
import sys;
import os;
import datetime;
import ConfigParser;
import json;

from multiprocessing  import Process, Queue, Lock;

from lib.scheduller   import Roundrobin;
from lib.amqp         import RabbitMQ_Publish, RabbitMQ_Consume;





###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE = '/etc/mct/mct_referee.ini';




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
                request = self.__queue.get(True, 5);
            except:
                request = '';
                pass;

            print "MESSAGE: " + str(request);

            if request:
                print('[LOG] Divisao %s recebeu a msg %s.',self.__div,request);

                ## When the div. receiving the message performs all tasks rela-
                ## ted to the action described in the message.
                self.__exec_action(request);

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
    def __exec_action(self, request):

        response = {
            'action': request['action'],
            'player': request['player'],
            'msg_id': request['msg_id'],
            'status': 'ok'
        }

        self.__publisher.publish(response, 'mct_dispatch');
        print '[LOG] enviado!';
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

        print '[LOG]: Gracefull stop ...';


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
        print '[LOG]: AMQP APP ID : ' + str(properties.app_id);

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        ## The json.loads translate a string containing JSON data into a Python
        ## value.
        message = json.loads(message);

        ## Check if the message received is valid. Verify all fields in the mes
        ## sage.
        #valRet = self.__inspect_request(messageDict);

        ##
        #divId = int(messageDict['div_id']);

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
        ## Verify other aspect from request.

        keywords = [
            'action',
            'player',
            'msg_id',
            'vmt_id',
            'div_id'
        ];

        for key in keywords:
             if not request.has_key(key):
                print "LOG: missed field " + key;
                return 1;

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

    try:
        ## LOG:
        print '[LOG]: EXECUTION STARTED....';
        mctReferee = MCT_Referee();
        mctReferee.consume();

    ## Caso Ctrl-C seja precionado realiza os procedimentos p/ finalizar o ambi
    ## ente.
    except KeyboardInterrupt, error:
        ## LOG:
        print '[LOG]: EXECUTION FINISHED...';
        mctReferee.gracefull_stop();

    sys.exit(0);
## EOF.

