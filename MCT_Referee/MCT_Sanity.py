#!/usr/bin/env python


import time;
import sys;
import os;
import datetime;
import json;
import logging;
import logging.handlers;
import hashlib;

from sqlalchemy                  import and_, or_;
from multiprocessing             import Process, Queue, Lock;
from mct.lib.amqp                import RabbitMQ_Publish, RabbitMQ_Consume;
from mct.lib.utils               import *;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy, Player, Vm;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE           = 'mct-sanity.ini';
HOME_FOLDER           = os.path.join(os.environ['HOME'], CONFIG_FILE);
RUNNING_FOLDER        = os.path.join('./'              , CONFIG_FILE);
DEFAULT_CONFIG_FOLDER = os.path.join('/etc/mct/'       , CONFIG_FILE);
NAME                  = 'mct-sanity';








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Sanity_Recv(Process, RabbitMQ_Consume):

    """
    Class MCT_Sanity: waiting responses by the VM information requests.
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    ** callback == waiting for requests.
    ** stop     == consume stop.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __db            = None;
    __print         = None;
    __publish       = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM cfg    == dictionary with configurations about MCT_Sanity.
    ## @PARAM logger == logger object.
    ## @PARAM db     == database descriptor.
    ##
    def __init__(self, cfg, logger, db):
        super(MCT_Sanity_Recv, self).__init__();

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, cfg['recv']);

        ## Set database reference.
        self.__db = db;

        ## LOG:
        self.__print.show("###### START MCT_SANITY RECV ######\n",'I');


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: method invoked when the pika receive a message.
    ## ------------------------------------------------------------------------
    ## @PARAM pika.Channel              channel    = the communication channel.
    ## @PARAM pika.spec.Basic.Deliver   method     = 
    ## @PARAM pika.spec.BasicProperties properties = 
    ## @PARAM str                       msg        = message received.
    ##
    def callback(self, channel, method, properties, msg):
        appId = properties.app_id;

        ## LOG:
        self.__print.show('MESSAGE RECEIVED: ' + msg + ' Id: '+ appId,'I');

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        ## The json.loads translate a string containing JSON data into a Python
        ## dictionary format.
        msg = json.loads(msg);

        ## Message handle:
        self.__message_handle(msg);

        ## LOG:
        self.__print.show('------------------------------------------\n', 'I');
        return SUCCESS;


    ##
    ## BRIEF: main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):
         ## Start the message consume:
         self.consume();

         return SUCCESS;


    ##
    ## BRIEF: consume stop.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        self.chn.basic_cancel(self.consumeTag);
        self.chn.close();
        self.connection.close();

        ## LOG:
        self.__print.show("###### STOP MCT_SANITY RECV ######\n",'I');
        return SUCCESS;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: handle the message.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message data.
    ##
    def __message_handle(self, msg):

        ## LOG:
        self.__print.show('RETURN FROM GETINF_INST IS '+str(msg['status']),'I');

        if msg['status'] == FAILED:

            ## Update the field status and instance time finished (timestamp).
            data = {
                'timestamp_finished' : str(datetime.datetime.now()),
                'status'             : CHEATING 
            };

            whereFilter = and_(Vm.origin_id    == msg['data']['origId'  ],
                               Vm.origin_add   == msg['data']['origAddr'],
                               Vm.origin_name  == msg['data']['origName'],
                               Vm.destiny_name == msg['destName']);

            self.__db['lock'].acquire();
            self.__db['db'  ].update_reg(Vm, whereFilter, data);
            self.__db['lock'].release();

            ## Update player perfil table:
            self.__update_used_values(msg);

        return SUCCESS;


    ##
    ## BRIEF: update all values of offer and used resources by division. 
    ## ------------------------------------------------------------------------
    ## @PARAM int  action  == increment (0) or decrement (1) usage.
    ##
    def __update_used_values(self, msg):

        ## Perform a select to get all vm instances assign (running) in vPlayer.
        self.__db['lock'].acquire();
        dRecv = self.__db['db'].all_regs_filter(Player,
                                             (Player.name == msg['destName']));
        self.__db['lock'].release();

        if dRecv != []:
            ## LOG:
            self.__print.show('UPDATE: VALRET: ' + str(dRecv), 'I');

            ## Calculate the decrement of resources to destiny player (who run-
            ## ning the instance).
            data = self.__decrement_value_database(dRecv[-1], msg);

            ## Update database:
            self.__db['lock'].acquire();
            self.__db['db'  ].update_reg(Player,Player.name == msg['destName'],data);
            self.__db['lock'].release();

        return SUCCESS;


    ##
    ## BRIEF: decrement player values.
    ## ------------------------------------------------------------------------
    ## @PARAM recv == values to update.
    ## @PARAM msg  == message received.
    ##
    def __decrement_value_database(self, recv, msg):

        record = {};

        ## Convert values:
        record['vcpus_used'   ] = int(recv['vcpus_used'   ]);
        record['memory_used'  ] = int(recv['memory_used'  ]);
        record['local_gb_used'] = int(recv['local_gb_used']);
        record['running'      ] = int(recv['running'      ]);
        record['finished'     ] = int(recv['finished'     ]);
        record['problem_del'  ] = int(recv['problem_del'  ]);
        record['vcpus_used'   ] -= int(msg['data']['vcpus']);
        record['memory_used'  ] -= int(msg['data']['mem'  ]);
        record['local_gb_used'] -= int(msg['data']['disk' ]);
        record['running'      ] -= 1;
        record['finished'     ] += 1;

        ## LOG:
        self.__print.show('VALUES UDPATE AFTER DEL' + str(record),'I');
        return record;
## END CLASS.








class MCT_Sanity_Send(Process):

    """
    Class MCT_Sanity_Send: send request by VMs status.
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __routeDispatch = None;
    __db            = None;
    __print         = None;
    __publish       = None;
    __name          = None;
    __myIp          = None;
    __time          = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM cfg    == dictionary with configurations about MCT_Sanity.
    ## @PARAM logger == logger object.
    ## @PARAM db     == database descriptor.
    ##
    def __init__(self, cfg, logger, db):
        super(MCT_Sanity_Send, self).__init__();

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## Get which route is used to deliver the message to the MCT_Dispatch.
        self.__routeDispatch = cfg['send']['route'];

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish = RabbitMQ_Publish(cfg['send']);

        ## Get MCT_Sanity name and address.
        self.__myIp = cfg['main']['myip'];
        self.__time = cfg['main']['time'];

        ## Set database reference.
        self.__db = db;

        ## LOG:
        self.__print.show("###### START MCT_SANITY SEND ######\n",'I');


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        while True:

            ## Get all entry in VM database that the status is 1 (running);
            self.__db['lock'].acquire();
            dRecv = self.__db['db'].all_regs_filter(Vm, (Vm.status == 1));
            self.__db['lock'].release();

            if dRecv != []:
        
                for vm in dRecv:
                   ## LOG:
                   self.__print.show("VM TO CHECK SANITY: " + str(vm) ,'I');

                   ## Create basic message to MCT_Dispatch. 
                   msg = self.__create_message();

                   ## Set information: 
                   msg['destAddr'] = vm['destiny_add' ];
                   msg['destName'] = vm['destiny_name'];

                   msg['data']['origAddr'] = vm['origin_add' ];
                   msg['data']['origName'] = vm['origin_name'];
                   msg['data']['origId'  ] = vm['origin_id'  ];
                   msg['data']['vcpus'   ] = vm['vcpus'      ];
                   msg['data']['mem'     ] = vm['mem'        ];
                   msg['data']['disk'    ] = vm['disk'       ];

                   ## Publish the message.
                   self.__publish.publish(msg, self.__routeDispatch);

                   ## LOG:
                   self.__print.show("PUBLISH THE MESSAGE: " + str(msg),'I');

                   ## LOG:
                   self.__print.show("------------------------------\n",'I');

            time.sleep(float(self.__time));

        return SUCCESS;


    ##
    ## BRIEF: process stop.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        ## LOG:
        self.__print.show("###### STOP MCT_SANITY SEND ######\n",'I');
        return SUCCESS;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: create a new index based in a hash.
    ## ------------------------------------------------------------------------
    ##
    def __create_index(self):

        ## Use FIPS SHA security algotirh sha512() to create a SHA hash object.
        newHash = hashlib.sha512();

        ## Update the hash object with the string arg. Repeated calls are equi-
        ## valent to a single call with the concatenation of all the arguments:
        newHash.update(str(time.time()));

        ## Return a hash with ten position:
        return newHash.hexdigest()[:10];



    ##
    ## BRIEF: create message to send.
    ## ------------------------------------------------------------------------
    ##
    def __create_message(self):

        index = 'mct-sanity_' + str(self.__create_index());

        message = {
            'code'    : SANITY_INSTANCE,
            'playerId': NAME,
            'status'  : 0,
            'reqId'   : index,
            'retId'   : index,
            'origAddr': self.__myIp,
            'destAddr': '',
            'destName': '',
            'data'    : {}
        };

        ## LOG:
        self.__print.show("CREATE MESSAGE TO SEND: " +str(message), 'I');

        return message;

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
    __cfg     = None;
    __logger  = None;
    __print   = None;
    __running = ['', ''];
    __db      = {};


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ##
    def __init__(self):

        ## Get the configurantion parameters.
        self.__cfg    = self.__get_configs();

        ## Configurate the logger. Use the parameters defineds in configuration
        ## file.
        self.__logger = self.__logger_setting(self.__cfg['log']);

        ## Connect to database.
        self.__get_database();


    ###########################################################################
    ## PUBLIC                                                                ##
    ###########################################################################
    ##
    ## BRIEF: start the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def start(self):
        ## Running vplayer in the thread:
        self.__running[0]=MCT_Sanity_Send(self.__cfg,self.__logger,self.__db);
        self.__running[0].daemon = True;
        self.__running[0].start();

        self.__running[1]=MCT_Sanity_Recv(self.__cfg,self.__logger,self.__db);
        self.__running[1].daemon = True;
        self.__running[1].start();

        for threadObject in self.__running:
            threadObject.join();

        return SUCCESS;


    ##
    ## BRIEF: stiop the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):

        ## Stop all virtual player executing in thread:
        try:
            ## SEND:
            self.__running[0].stop();
            self.__running[0].terminate();
            self.__running[0].join();

            ## RECV:
            self.__running[1].stop();
            self.__running[1].terminate();
            self.__running[1].join();
        except:
            pass;

        return SUCCESS;


    ###########################################################################
    ## PRIVATE                                                               ##
    ###########################################################################
    ##
    ## BRIEF: connect to database.
    ## ------------------------------------------------------------------------
    ##
    def __get_database(self):

        ## Connect to database (use the crendetiais defined in the cfg file):
        self.__db['db'] = MCT_Database_SQLAlchemy(self.__cfg['database']);

        ## A primitive lock is a synchronization primitive that is not owned by
        ## by a particular thread when locked.
        self.__db['lock'] = Lock();

        return 0;


    ##
    ## BRIEF: get configuration from config file.
    ## ------------------------------------------------------------------------
    ##
    def __get_configs(self):
        cfgFileFound = '';

        ## Lookin in three places:
        ## 1 - user home.
        ## 2 - running folder.
        ## 3 - /etc/mct/
        for cfgFile in [HOME_FOLDER, RUNNING_FOLDER, DEFAULT_CONFIG_FOLDER]:
            if os.path.isfile(cfgFile):
                cfgFileFound = cfgFile;
                break;

        if cfgFileFound == '':
            raise ValueError('CONFIGURATION FILE NOT FOUND IN THE SYSTEM!');

        return get_configs(cfgFileFound);


    ## 
    ## BRIEF: setting logger parameters.
    ## ------------------------------------------------------------------------
    ## @PARAM settings == logger configurations.
    ##
    def __logger_setting(self, settings):

        ## Create a handler and define the output filename and the max size and
        ## max number of the files (1 mega = 1048576 bytes).
        handler = logging.handlers.RotatingFileHandler(
                                  filename    = settings['log_filename'],
                                  maxBytes    = int(settings['file_max_byte']),
                                  backupCount = int(settings['backup_count']));

        ## Create a foramatter that specific the format of log and insert it in
        ## the log handler. 
        formatter = logging.Formatter(settings['log_format']);
        handler.setFormatter(formatter);

        ## Set up a specific logger with our desired output level (in this case
        ## DEBUG). Before, insert the handler in the logger object.
        logger = logging.getLogger(settings['log_name']);
        logger.setLevel(logging.DEBUG);
        logger.addHandler(handler);

        return logger;

## END CLASS.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    try:
        main = Main();
        main.start();

    except ValueError as exceptionNotice:
        print exceptionNotice;

    except KeyboardInterrupt:
        main.stop();
        print "BYE!";

    sys.exit(0);
## EOF.
