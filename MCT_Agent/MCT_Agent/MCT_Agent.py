#!/usr/bin/env python


import ConfigParser;
import sys;
import json;
import time;


from lib.amqp         import RabbitMQ_Publish, RabbitMQ_Consume;
from multiprocessing  import Process;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CFG_FILE = '../../mct_agent.ini';






###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Comunication(RabbitMQ_Consume):

    """
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __route = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, cfgConsume, cfgPublish):

        self.__route = cfgPublish['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, cfgConsume);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publisher = RabbitMQ_Publish(cfgPublish);
        

    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
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
        print '[LOG]: FROM ' + str(properties.app_id);

        ## Convert the json format to a structure than can handle by the python
        message = json.loads(message);

        ##
        self.__send_message(message);

        self.chn.basic_ack(method.delivery_tag);
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: sends the message to a queue.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __send_message(self, request):

        ## LOG:
        print '[LOG] REQUEST RECEIVED: ' + str(request);
        print '[LOG] SEND MESSAGE!'

        ##
        self.__publisher.publish(request, self.__route);
        return 0;
## END.






class Main(Process):

    """
    ---------------------------------------------------------------------------
    """


    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __cfg = None;
    __amq = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, typeConsume):
        super(Main, self).__init__();

        self.__cfg = {};

        ## Obtain all configs itens:
        self.__get_config(CFG_FILE);

        ##
        #cfgPublishA = self.__cfg['amqp_publish_loc'];
        cfgPublishExt = self.__cfg['amqp_external_publish'];
        cfgConsumeExt = self.__cfg['amqp_external_consume'];

        cfgPublishInt = self.__cfg['amqp_internal_publish'];
        cfgConsumeInt = self.__cfg['amqp_internal_consume'];

        ##
        if   typeConsume == 'A':
            self.__amq = MCT_Comunication(cfgConsumeInt, cfgPublishExt);

        elif typeConsume == 'D':
            self.__amq = MCT_Comunication(cfgConsumeExt, cfgPublishInt);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def run(self):
        self.__amq.consume();


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: obtain all configuration from conffiles.
    ## ------------------------------------------------------------------------
    ## @PARAM str cfgFile == conffile name.
    ##
    def __get_config(self, cfgFile):

       config = ConfigParser.ConfigParser();
       config.readfp(open(cfgFile));

       for section in config.sections():
           self.__cfg[section] = {};

           for option in config.options(section):
               self.__cfg[section][option] = config.get(section, option);

       return 0;
## END.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    try:
        daemonA = Main('A');
        daemonA.daemon = True;
        daemonA.start();

        daemonD = Main('D');
        daemonD.daemon = True;
        daemonD.start();

        while True:
            time.sleep(5);

    ## Caso Ctrl-C seja precionado realiza os procedimentos p/ finalizar o ambi
    ## ente.
    except KeyboardInterrupt, error:
        daemonA.terminate();
        daemonA.join();

        daemonD.terminate();
        daemonD.join();
## EOF
