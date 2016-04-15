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
CFG_FILE = '/etc/mct/mct_agent.ini';








###############################################################################
## PROCEDURES                                                                ##
###############################################################################
##
## BRIEF: obtain all configuration from conffiles.
## ---------------------------------------------------------------------------
## @PARAM str cfgFile == conffile name.
##
def get_config(cfgFile):
   cfg = {};

   config = ConfigParser.ConfigParser();
   config.readfp(open(cfgFile));

   for section in config.sections():
       cfg[section] = {};

       for option in config.options(section):
           cfg[section][option] = config.get(section, option);

   return cfg;
## END.








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Agent(RabbitMQ_Consume):

    """
    
    ---------------------------------------------------------------------------
    callback == method invoked when the pika receive a message.
    
    __recv_message_referee == receive message from referee.
    __send_message_referee == send message to referee.
    __valid_request        == check if all necessary fields are in request.

    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __route   = None;
    __publish = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, cfgConsume, cfgPublish):

        ## Get which route is used to deliver the msg to the 'correct destine'.
        self.__route = cfgPublish['route'];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, cfgConsume);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish=RabbitMQ_Publish(cfgPublish);
        

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

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        ## Convert the json format to a structure than can handle by the python
        message = json.loads(message);

        ## Check if is a request received from players or a return from a divi-
        ## sions. The identifier is the properties.app_id.
        if properties.app_id == 'MCT_Dispatch':
            if self.__valid_request(message) == 0:
                self.__recv_message_dispatch(message, properties.app_id);
        else:
            if self.__valid_request(message) == 0:
                self.__send_message_dispatch(message, properties.app_id);

        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: send message to MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __send_message_dispatch(self, request, appId):

        ## LOG:
        print '[LOG]: REQUEST RECEIVED: ' + str(request);
        print '[LOG]: SEND MESSAGE!'

        ##
        self.__publish.publish(request, self.__route);
        return 0;


    ##
    ## BRIEF: receive message from MCT_Dispatch.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __recv_message_dispatch(self, request, appId):

        ## LOG:
        print '[LOG]: REQUEST RECEIVED FROM: ' + str(appId);
        print '[LOG]: MESSAGE RECEIVED!'

        ##
        ##self.__publish.publish(request, self.__route);
        return 0;


    ##
    ## BRIEF: check if all necessary fields are in the request.
    ## ------------------------------------------------------------------------
    ## @PARAM dict request == received request.
    ##
    def __valid_request(self, request):
        ## TODO: DEFINR FORMATO!

        ## LOG:
        print '[LOG]: DEFINIR FORMATO!';
        return 0;

## END.






class Main(Process):

    """
    ---------------------------------------------------------------------------
    run == execute the process.
    """


    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __amq = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, typeConsume):
        super(Main, self).__init__();

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        config = get_config(CFG_FILE);

        if   typeConsume == 'EXTERNAL':
            self.__amq = MCT_Agent(config['amqp_internal_consume'],
                                   config['amqp_external_publish']);

        elif typeConsume == 'INTERNAL':
            self.__amq = MCT_Agent(config['amqp_external_consume'],
                                   config['amqp_internal_publish']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: execute the process.
    ## ------------------------------------------------------------------------
    ##
    def run(self):
        self.__amq.consume();
## END.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    ## LOG:
    print '[LOG]: EXECUTION STARTED...';

    ## Get all configs parameters presents in the config file localized in CFG_
    ## FILE path.
    config = get_config(CFG_FILE);
   
    try:
        processes = [];
        for pType in ['EXTERNAL', 'INTERNAL']:
            process = Main(pType);
            process.daemon = True;
            process.start();
            processes.append(process);

        while True:
            time.sleep(float(config['main']['pooling_time_interval']));

    ## Caso Ctrl-C seja precionado realiza os procedimentos p/ finalizar o ambi
    ## ente.
    except KeyboardInterrupt, error:
        ## LOG:
        print '[LOG]: EXECUTION FINISHED...';

        for process in processes:
            process.terminate();
            process.join();

    sys.exit(0);
## EOF
