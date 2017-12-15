#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
from __future__        import with_statement;

import ConfigParser;
import hashlib;
import time;
import random;
import ast;
import logging;
import logging.handlers;
import sys;
import socket;
import json;
import pika;
import threading;
import mysql;
import yaml;
import os;

from sqlalchemy                  import and_, or_;
from threading                   import Timer;
from multiprocessing             import Process, Queue, Lock;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy, Request, Player;
from mct.lib.utils               import *;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE  = '/etc/mct/mct-simulation.ini';
LOG_NAME     = 'MCT_Driver_Simulation';
LOG_FORMAT   = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME = '/var/log/mct/mct_driver_simulation.log';
N_FACTOR     = 1 
N_VALUE      = 610
INTERVAL     = 60




###############################################################################
## LOG                                                                       ##
###############################################################################
logging.basicConfig()

## Create a handler and define the output filename and the max size and max nun
## ber of the files (1 mega = 1048576 bytes).
handler= logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                              maxBytes=10485760,
                                              backupCount=100);

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
## FUNCTION                                                                  ##
###############################################################################
##
## BRIEF: mantain the virtual player state.
## ----------------------------------------------------------------------------
## @PARAM vPlayerName  == virtual player name.
## @PARAM db           == database connection.
##
##
def get_virtual_player_state(vPlayerName, db):

     stateDictionary = {
         'vPlayer': vPlayerName,
         'vmsRcv' : [],
         'vmsSnd' : []
     };

     ## Perform a select to get all vm instances assign (running) in 'vPlayer'.
     dataReceived = db['db'].all_regs_filter(State,  
                         State.player_id == vPlayerName and State.running == 1);

     if dataReceived != []:
         for vm in dataReceived:
             if vm['player_id'] == vPlayerName:
                 stateDictionary['vmsRcv'].append(vm);
             else:
                 stateDictionary['vmsSnd'].append(vm);

     return stateDictionary;

## END DEFINITION.







###############################################################################
## CLASSES                                                                   ##
###############################################################################
class Repeated_Timer(object):

    """
    Class Repeated_Timer: execute the action in time interval.
    ---------------------------------------------------------------------------
    PUBLIC METHODS
    ** start == start the process.
    ** stop  == stop  the process.
    """

    ###########################################################################
    ## ATRIBUTES                                                             ##
    ###########################################################################
    function   = None;
    args       = None;
    kwargs     = None;
    is_running = None;
    __interval = None;
    __timer    = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM interval == time interval to execute the action.
    ## @PARAM function == function to execute (action).
    ## @PARAM *args    == function arguments.
    ## @PARAM **kwargs == function arguments.
    ##
    def __init__(self, interval, function, *args, **kwargs):

        ## Set all attributes correct execution:
        self.function   = function;
        self.args       = args;
        self.kwargs     = kwargs;
        self.is_running = False;
        self.__interval = interval;

        ## Start the execution: 
        self.start();


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: start the process.
    ## ------------------------------------------------------------------------
    ##
    def start(self):
        if not self.is_running:
            self.__timer = Timer(self.__interval, self.__run)
            self.__timer.start()
            self.is_running = True;


    ##
    ## BRIEF: stop the process.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        self.__timer.cancel();
        self.is_running = False;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: block to running in thread. 
    ## ------------------------------------------------------------------------
    ##
    def __run(self):
        self.is_running = False;
        self.start();
        self.function(*self.args, **self.kwargs);

## END OF CLASS








class MCT_Simple_AMQP_Publish:

    """
    Class MCT_Simple_AMQP_PUBLISH:perform the publish to the MCT_Agent service.
    --------------------------------------------------------------------------
    PUBLIC METHODS:
    ** publish  == publish a message by the AMQP to MCT_Agent.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __exchange     = None;
    __route        = None;
    __channel      = None;
    __print        = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM cfg    == dictionary with MCT_Simple_AMPQ_Publish configuration.
    ## @PARAM logger == log object.
    ##
    def __init__(self, cfg, logger):

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['print'], logger);

        ## LOG:
        self.__print.show('INITIALIZE COMMUNICATION OBJECT', 'I');

        self.__exchange = cfg['exchange'];
        self.__route    = cfg['route'   ];

        credentials = pika.PlainCredentials(cfg['user'], cfg['pass']);

        ## Connection parameters object that is passed into the connection ada-
        ## pter upon construction. 
        parameters = pika.ConnectionParameters(host        = cfg['address'],
                                               credentials = credentials);

        ## The BlockingConnection creates a layer on top of Pika's asynchronous
        ## core providing methods that will block until their expected response
        ## has returned. 
        connection = pika.BlockingConnection(parameters);

        ## Create a new channel with the next available channel number or pass
        ## in a channel number to use. 
        self.channel = connection.channel();

        ## This method creates an exchange if it does not already exist, and if
        ## the exchange exists, verifies that it is of the correct and expected
        ## class.
        self.channel.exchange_declare(exchange=cfg['exchange'], type='direct');

        ## Confirme delivery.
        self.channel.confirm_delivery;


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: publish a message by the AMQP to MCT_Agent.
    ## ------------------------------------------------------------------------
    ## @PARAM message = data to publish.
    ##
    def publish(self, message):

        ## LOG:
        self.__print.show('PUBLISH MESSAGE: ' + str(message), 'I');

        propertiesData = {
            'delivery_mode': 2,
            'app_id'       : 'Agent_Drive',
            'content_type' : 'application/json',
            'headers'      : message
        }

        properties = pika.BasicProperties(**propertiesData);

        ## Serialize object to a JSON formatted str using this conversion table
        ## If ensure_ascii is False, the result may contain non-ASCII characte-
        ## rs and the return value may be a unicode instance.
        jData = json.dumps(message, ensure_ascii=False);

        ## Publish to the channel with the given exchange,routing key and body.
        ## Returns a boolean value indicating the success of the operation.
        try:
            ack = self.channel.basic_publish(self.__exchange, 
                                             self.__route, jData, properties);

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError), error:
            ack = -1;

        return ack;
## END OF CLASS









class MCT_Action(object):

    """
    Class MCT_Action: interface layer between MCT_Agent service and MCT_Drive.
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    ** dispatch          == receive request.
    ** get_resources_inf == set the resources from player's division.
    ** set_resources_inf == set the resources avaliable.
    ** create_instance   == create a new instance via MCT.
    ** delete_instance   == delete remote instance.
    """


    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    state           = None;
    data            = None;
    __dbConnection  = None;
    __myIp          = None;
    __print         = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM vCfg   == configuration dictionary.
    ## @PARAM db     == connection with database.
    ## @PARAM logger == log object.
    ##
    def __init__(self, vCfg, db, logger):
        
        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(vCfg['print'], logger);

        ## Get which route is used to deliver the msg to the 'correct destine'.
        self.__route = vCfg['amqp_route'];

        ## Get player identifier:
        self.__name = vCfg['name'];

        ## Iteraction number and time to wainting response between iteractions.
        self.__requestPendingWaiting = float(vCfg['request_pending_waiting']);
        self.__requestPendingIteract =   int(vCfg['request_pending_iteract']);

        amqpConfig = {
            'user'      : vCfg['amqp_user'      ],
            'pass'      : vCfg['amqp_pass'      ],
            'route'     : vCfg['amqp_route'     ],
            'identifier': vCfg['amqp_identifier'],
            'address'   : vCfg['amqp_address'   ],
            'exchange'  : vCfg['amqp_exchange'  ],
            'queue'     : vCfg['amqp_queue_name'],
            'print'     : vCfg['print'          ]
        }

        ##
        self.__myIp = vCfg['agent_address'];

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish = MCT_Simple_AMQP_Publish(amqpConfig, logger);

        ## Intance a new object to handler all operation in the local database.
        self.__db = db;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def __getitem__(self, key):
        return getattr(self, key)


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: receive request.
    ## ------------------------------------------------------------------------
    ## @PARAM action == action to execute.
    ## @PARAM data   == dictionary with data to dispatch.
    ##
    def dispatch(self, action, data):
       dataReceived = {};

       ##
       if   action == ADD_REG_PLAYER:
           dataReceived = self.addreg_vplayer(data);

       elif action == DEL_REG_PLAYER:
           dataReceived = self.delreg_vplayer(data);

       ## Get resouces information from mct_referee. 
       if   action == GETINF_RESOURCE:
           dataReceived = self.getinf_resource();

       ## Set resources information to  mct_referee.
       elif action == SETINF_RESOURCE:
           dataReceived = self.setinf_resource(data);

       ## Create a 'virtual' server in remote hosts.
       elif action == CREATE_INSTANCE:
           dataReceived = self.create_instance(data);

       ## Delete a 'virtual' server in remote hosts.
       elif action == DELETE_INSTANCE:
           dataReceived = self.delete_instance(data);

       return dataReceived;


    ##
    ## BRIEF: Get the resources from player's division.
    ## ------------------------------------------------------------------------
    ##
    def getinf_resource(self):

        ## LOG:
        self.__print.show('GETTING MCT RESOURCE INFORMATION!', 'I');

        ## Create an idx to identify the request for the resources information.
        idx = self.__name + '_' + self.__create_index();

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(GETINF_RESOURCE, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dataReceived = self.__waiting_return(self.__name, idx);
        else:
            dataReceived = {};

        ## LOG:
        self.__print.show('|GETINF| - data received: '+str(dataReceived), 'I');

        ## Return the data:
        return dataReceived;


    ##
    ## BRIEF: Set the resources avaliable.
    ## ------------------------------------------------------------------------
    ## @PARAM data == specific data to send.
    ##
    def setinf_resource(self, data):

        ## LOG:
        self.__print.show('SETING MCT RESOURCE INFORMATION!', 'I');

        ## Create an idx to identify the request for the resources information.
        idx = self.__name + '_' + self.__create_index();

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(SETINF_RESOURCE, idx);

        msgToSend['data'] = {
            'vcpus'   : data['vcpus'   ],
            'memory'  : data['memory'  ],
            'local_gb': data['local_gb']
        }

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dataReceived = self.__waiting_return(self.__name, idx);
        else:
            dataReceived = {};

        ## LOG:
        self.__print.show('|SETINF| - data received: '+str(dataReceived), 'I');

        ## Return the data:
        return dataReceived;


    ##
    ## BRIEF: create a new instance via MCT.
    ## ------------------------------------------------------------------------
    ## @PARAM data == specific data to send.
    ##
    def create_instance(self, data):

        ## LOG:
        self.__print.show('SEND REQUEST TO CREATE A NEW INSTANCE!', 'I');

        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = self.__name + '_' + str(data['machineID']);

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(CREATE_INSTANCE, idx);

        msgToSend['data'] = {
           'name'  : idx,
           'uuid'  : idx,
           'flavor': FLV_NAME[data['vmType']],
           'vcpus' : CPU_INFO[data['vmType']],
           'mem'   : MEM_INFO[data['vmType']],
           'disk'  : DSK_INFO[data['vmType']],
           'image' : IMG_NAME,
           'net'   : NET_NAME 
        }

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dataReceived = self.__waiting_return(self.__name, idx);
        else:
            dataReceived = {};

        ## LOG:
        self.__print.show('|CREATE| - data received: '+str(dataReceived), 'I');

        ## Returns the data:
        return dataReceived;

 
    ##
    ## BRIEF: delete remote instance.
    ## ------------------------------------------------------------------------
    ## @PARAM data == specific data to send.
    ##
    def delete_instance(self, data):

        ## LOG:
        self.__print.show('SEND REQUEST TO DELETE AN INSTANCE!', 'I');

        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = self.__name + '_' + str(data['machineID']);

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(DELETE_INSTANCE, idx);

        msgToSend['data'] = {
           'name'  : idx,
           'uuid'  : idx
        }

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dataReceived = self.__waiting_return(self.__name, idx);
        else:
            dataReceived = {};

        ## LOG:
        self.__print.show('|DELETE| - data received: '+str(dataReceived), 'I');

        ## Returns the data:
        return dataReceived;


    ##
    ## BRIEF: register the player - get the token.
    ## ------------------------------------------------------------------------
    ## @PARAM data == specific data to send.
    ##
    def addreg_vplayer(self, data):

        ## LOG:
        self.__print.show('REGISTER THE PLAYER ' +self.__name+ ' IN MCT', 'I');

        ## Create an idx to identify the request for the resources information.
        idx = self.__name + '_' + self.__create_index();

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(ADD_REG_PLAYER, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dataReceived = self.__waiting_return(self.__name, idx);
        else:
            dataReceived = {};

        ## LOG:
        self.__print.show('|REGISTER| - data received: '+str(dataReceived), 'I');

        ## Returns the data:
        return dataReceived;
 

    ##
    ## BRIEF: unregister the player.
    ## ------------------------------------------------------------------------
    ## @PARAM data == specific data to send.
    ##
    def delreg_vplayer(self, data):
        return {};


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: Waiting for the answer is ready in database.
    ## ------------------------------------------------------------------------
    ## @PARAM str playerId  = identify of the player.
    ## @PARAM str requestId = identify of the resquest.
    ##
    def __waiting_return(self, playerId, requestId):
        count = 0;

        ## Waiting for the answer arrive. When the status change status get it.
        while True and count < self.__requestPendingIteract:

            ## Create filter:
            fColumns = and_(Request.player_id  == str(playerId) , 
                            Request.request_id == str(requestId));

            with self.__db['lock']:
                dRecv = self.__db['db'].all_regs_filter(Request, fColumns);

            if dRecv != []:

                valRet = {
                    'status': int(dRecv[-1]['status']),
                    'action': int(dRecv[-1]['action']),
                    'data'  : ast.literal_eval(dRecv[0]['message'])
                };

                ## Update the "player' satisfaction" level. Verify the status.
                if dRecv[-1]['action'] == CREATE_INSTANCE:
                    self.__fairness(dRecv[-1]['status'], dRecv[-1]['data']);

                return valRet;

            ## Wating for a predefined time to check (pooling) the list again.
            time.sleep(self.__requestPendingWaiting);
            count += 1;

            ## LOG:
            self.__print.show('WAITING FOR REQUEST RETURN: ' + requestId, 'I');

        return {};        


    ##
    ## BRIEF: calculate the player's fairness level.
    ## ------------------------------------------------------------------------
    ## @PARAM str status == status from action.
    ## @PARAM str data   == data received from agent.
    ##
    def __fairness(self, status, data):

        ## Create filter.
        fColumns = (Player.name == self.__name);

        ## Select the requests number and calculate the fairness! Mount the se-
        ## lect query.
        with self.__db['lock']:
            dReceived = self.__db['db'].all_regs_filter(Player, fColumns);

        accepts = int(dReceived[-1]['accepts']);
        rejects = int(dReceived[-1]['rejects']);
        
        totalRequest = accepts + rejects;

        ## Status "1" meaning that request for VM was accept by remote player!
        if status == 1:
            accepts += 1;
        else:
            rejects += 1;

        try:
            ## Caculate the porcetage:
            fairness = float((accepts*100)/requests);
        except:
            fairness = 0.0;
                
        data = {
            'name'     : self.__name,
            'accepts'  : accepts,
            'rejects'  : rejects,
            'fairness' : fairness
        };

        ## Update player status:
        with self.__db['lock']:
            self.__db['db'].update_reg(Player,Player.name == self.__name,data);
            
        ## LOG:
        self.__print.show(self.__name + ' REJECTS : | ' + str(rejects ), 'I');
        self.__print.show(self.__name + ' ACCEPTS : | ' + str(accepts ), 'I');
        self.__print.show(self.__name + ' FAIRNESS: | ' + str(fairness), 'I');

        return 0;

 
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
    ## BRIEF: create basic message to send.
    ## ------------------------------------------------------------------------
    ## @PARAM int action = action code.
    ## @PARAM str index  = artefact index.
    ##
    def __create_basic_message(self, action, index):
        message = {
            'code'    : action,
            'playerId': self.__name,
            'status'  : 0,
            'reqId'   : index,
            'retId'   : '',
            'origAddr': self.__myIp,
            'destAddr': '',
            'destName': '',
            'data'    : {}
        };

        return message;
## END CLASS.








class MCT_States:

    '''
    Class MCT_State: generate the state to execute.
    --------------------------------------------------------------------------
    '''

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __pools = {};
    __state = None;
    __print = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM vCfg   == virtual player configuration.
    ## @PARAM logger == log object.
    ##
    def __init__(self, vCfg, logger):
  
       ## Get the option that define to where the logs will are sent to show.
       self.__print = Show_Actions(vCfg['print'], logger);

       self.__addr   = vCfg['addr'  ];
       self.__port   = vCfg['port'  ];

       self.__messageDictSend = {
           'authentication' : '',
           'action'         : '',
           'player'         : vCfg['name']
       }


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: return one state (in str) from the database.
    ## ------------------------------------------------------------------------
    ##
    def give_me_state_from_database(self):
        mDictRecv = {'valid': 2};

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            ## Connect the client socket to the address and port where the ser-
            ## ver is listening
            sock.connect((self.__addr, int(self.__port)));

            ## Convert the python dictionary with data values to 'JSON' format.
            mJsonSend = json.dumps(self.__messageDictSend, ensure_ascii=False);

            ## Send data to MCT_DB_Proxy:
            sock.sendall(mJsonSend);

            ## Look for the response:
            mJsonRecv = sock.recv(1024);

            ## Load the JSON msg.Convert from JSON format to simple dictionary.
            mDictRecv = json.loads(mJsonRecv);

        except socket.error as error:
            ## LOG:
            self.__print.show('CONNECT TO MCT_DB_PROXY: ' + str(error), 'E');
            mDictRecv = {'valid': 2};

        finally:
            sock.close();

        return mDictRecv;
## END CLASS.








class MCT_VPlayer(Process):

    '''
    Class MCT_Emulation: emulation the player.
    ---------------------------------------------------------------------------
    PUBLICH METHODS
    ** run == main loop.
    '''

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __mctAction               = None;
    __mctStates               = None;
    __name                    = None;
    __addr                    = None;
    __lock                    = None;
    __dbConnection            = None;
    __get_resources_info_time = None;
    __set_resources_info_time = None;
    __get                     = True;
    __interval                = None;
    __vcpu                    = None;
    __memo                    = None;
    __disk                    = None;
    __print                   = None;
    __token                   = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM vCfg   == configuration file.
    ## @PARAM db     == connection with database.
    ## @PARAM logger == log object.
    ##
    def __init__(self, vCfg, db, logger):

        super(MCT_VPlayer, self).__init__();

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(vCfg['print'], logger);

        ## Player name and address:
        self.__name = vCfg['name'];
        self.__addr = vCfg['agent_address'];

        ## LOG:
        self.__print.show('INITIALIZE VPLAYER: ' + self.__name, 'I');

        ## Set the objet that represent the connection with database (is neces-
        ## sary to use the lock object).
        self.__db = db;

        ## Instance object that generate actions that will be send to MCT_Agent
        self.__mctStates = MCT_States(vCfg, logger);

        ## Instance object that send actions generate by State to the MCT_Agent
        self.__mctAction = MCT_Action(vCfg, self.__db, logger);

        ## Time to send get resource info and set resources info request to MCT
        ## referee:
        self.__interval = float(vCfg['get_set_resources_info_time']);

        ## The localization and name of the file with the resources information
        self.__resourcesFile = vCfg['resources_file'];


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        ## Register this virtual player. If the process is sucesfull get a to-
        ## ken to comunication with MCT.
        try:
            self.__token = self.__addreg_me();
        except:
            ## LOG:
            self.__print.show('IMPOSSIBLE GET TOKEN: ' + self.__name, 'E');
            return 1;

        oldTime = 0;

        ## Set virtual players resources: 
        self.__set_resources_info();

        ## Scheduller set and get information action t/from MCT main components.
        getSetInfRepeat = Repeated_Timer(self.__interval, self.__get_set_info);

        while True:

            ## Get a new action from database through the MCT_DB_Proxy service.
            data = self.__mctStates.give_me_state_from_database();
      
            if data['valid'] != 2:

                if   data['action'] == 0:
                     action = CREATE_INSTANCE;
                elif data['action'] == 1:
                     action = DELETE_INSTANCE;

                ## Calculate the new time to waiting until perform new action.
                newTime = float(data['time']/(N_VALUE*N_FACTOR)) - oldTime; 
                oldTime = newTime;

                if newTime < 1.0:
                    newTime = 1;

                ## Wait X seconds to dispatich a new action to the 'MCT_Agent'.
                time.sleep(float(newTime));
                   

                ## Dispatch the action to MCT_Dispatch:
                dataRecv = self.__mctAction.dispatch(action, data);

            else:
                getSetInfRepeat.stop();
                break;

        ## LOG:
        self.__print.show('END SIMULATION PLAYER: ' + self.__name, 'I');
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: send request to get and set information.
    ## ------------------------------------------------------------------------
    ##
    def __get_set_info(self):

        ## Check the last action. If was get execute the set information, other
        ## wise execute the get. 
        if self.__get == True:
            self.__set_resources_info();
        else:
            self.__get_resources_info();

        ## Select the next action: 'True' to 'False', 'Get to Set' information.
        self.__get = not self.__get;


    ##
    ## BRIEF: get tournament information.
    ## ------------------------------------------------------------------------
    ##
    def __get_resources_info(self):

        ## LOG:
        self.__print.show('SEND REQUEST TO GET TOURNAMENT INFORMATION!','I');

        ## Send the request to get information to the MCT_Dispatch in the remo-
        ## te server.
        dataRecv = self.__mctAction.dispatch(GETINF_RESOURCE, {});


    ##
    ## BRIEF: set vplayer information to the tournament.
    ## ------------------------------------------------------------------------
    ##
    def __set_resources_info(self):

        errorDatabase = False;

        ## Obtain the dictionary with resource informations (vcpus, memory, and
        ## disk).
        try:
            rDict = yaml.load(file(self.__resourcesFile, 'r')); 

            data = {
                'vcpus'        : rDict['vcpus'       ],
                'memory'       : rDict['memory'      ],
                'local_gb'     : rDict['local_gb'    ],
                'max_instance' : rDict['max_instance']
            };

            ## Execute in exclusive mode-lock block-the database update action.
            with self.__db['lock']:
                self.__db['db'].update_reg(Player, Player.name == self.__name, data); 

            ## Send the request to update 'resources' values to 'MCT_Dispatch':
            dataRecv = self.__mctAction.dispatch(SETINF_RESOURCE, data);

            ## LOG:
            self.__print.show('UPDATE RESOURCE VALUES IN TABLE!','I');
            return 0;

        except yaml.reader.ReaderError:
            pass;

        return 1;


    ##
    ## BRIEF: register virtual player.
    ## ------------------------------------------------------------------------ 
    ##
    def __addreg_me(self):
        ## Send the request:
        dReceived = self.__mctAction.dispatch(ADD_REG_PLAYER, {});

        ## Get the token:
        try:
            token = dReceived['data']['token'];
        except:
             ## LOG:
             self.__print.show('ERROR TO PARSE THE TOKEN!','I');
             return {};
        
        try:
            ## Insert the player in database:
            player = Player();

            player.name     = self.__name;
            player.address  = self.__addr;
            player.division = 0;
            player.token    = token;

            valRet = self.__db['db'].insert_reg(player);

        except:
            ## LOG:
             self.__print.show('VPLAYER YET INSERTED IN LOCAL BASE!', 'I');

        return token;


    ##
    ## BRIEF: register virtual player.
    ## ------------------------------------------------------------------------ 
    ##
    def __delreg_me(self):
        ## Send the request:
        dataRecv = self.__mctAction.dispatch(DELREG_PLAYER, {});

        return dataRecv;
## END CLASS.








class MCT_Drive_Simulation:
    """
    Class MCT_Drive_Simulation: main class in the module.
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __vPlayers           = [];
    __db                 = {};
    __cfg                = None;
    __print              = None;
    __publish            = None;
    __virtualPlayersPath = None;
    __vRunning           = {};


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM logger    == log object.
    ##
    def __init__(self, logger):
   
        ## Try open and obtain all configs about the MCT_Drive_Simulation exe-
        ## cution.
        self.__get_configs(CONFIG_FILE);

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(self.__cfg['main']['print'], logger);

        ## Connect to database.
        self.__get_database();

        ## Obtain configuration options to the virtual player (amqp cfg, etc).
        self.__virtualPlayersPath = self.__cfg['vplayers']['dir'];


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: excute the MCT_Drive_Simulation.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        ## LOG:
        self.__print.show("\n####### START MCT_DRIVE_SIMULATION #######\n",'I');

        while True:

            for vPlayer in os.listdir(self.__virtualPlayersPath):
                try:
                    ## Open virtual player config:
                    vCfg = yaml.load(file('/etc/mct/vplayers/' + vPlayer, 'r'));
                except yaml.reader.ReaderError:
                    pass;

                if vCfg['enable'] == 1:
                    ## Check if player already in the vplayer excuting list.
                    if self.__vplayer_in_running_list(vCfg) == False:
                        self.__add_vplayer(vCfg);

                else:
                    ## Check if player already in the vplayer excuting list.
                    if self.__vplayer_in_running_list(vCfg) == True:
                        self.__del_vplayer(vCfg);

            ## Wait an unpredicable time.Insert some entropy in the enviroment.
            mutable_time_to_waiting(5.0, 10.0);

            if self.__vRunning == {}:
                return False;

            ## LOG:
            self.__print.show("EXECUTE A LOOP", 'I');

        return True;


    ##
    ## BRIEF: stop the execution.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):

        ## LOG:
        self.__print.show("\n###### FINISH MCT_DRIVE_SIMULATION ######\n",'I');

        ## Stop all virtual player executing in thread:
        for vPlayer in  self.__vRunning:
            self.__vRunning[vPlayer].terminate();
            self.__vRunning[vPlayer].join();

        return True;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: get configuration from config file.
    ## ------------------------------------------------------------------------
    ##
    def __get_configs(self, cfgFileName):

        try:
            self.__cfg = get_configs(cfgFileName);
            return 0;

        except ConfigParser.Error as cfgError:
            print '[E] IT IS IMPOSSIBLE OBTAIN CFGS: ' + str(cfgError);
            sys.exit(1);


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
    ## BRIEF: check if the vplayer is in list and running.
    ## ------------------------------------------------------------------------
    ## @PARAM vCfg == virtual player configuration.
    ##
    def __vplayer_in_running_list(self, vCfg):
 
        if self.__vRunning.has_key(vCfg['name']) == True:
            ## Verify if the thread is running:
            if self.__vRunning[vCfg['name']].is_alive() == True:
                return True;

        return False;


    ##
    ## BRIEF: launch a vplayer.
    ## ------------------------------------------------------------------------ 
    ## @PARAM vCfg == virtual player configuration.
    ##
    def __add_vplayer(self, vCfg):

        ## LOG:
        self.__print.show("Player to register: " + str(vCfg),'I');

        ## Running vplayer in the thread:
        self.__vRunning[vCfg['name']]=MCT_VPlayer(vCfg, self.__db, logger);
        self.__vRunning[vCfg['name']].daemon = True;
        self.__vRunning[vCfg['name']].start();

        return True;


    ##
    ## BRIEF: remove a vplayer.
    ## ------------------------------------------------------------------------ 
    ## @PARAM vCfg == virtual player configuration.
    ##
    def __del_vplayer(self, vCfg):

        ## Stop vplayer:
        self.__vRunning[vCfg['name']].terminate();
        self.__vRunning[vCfg['name']].join();

        ## Remove entry:
        del self.__vRunning[vCfg['name']];

        return True;
## END CLASS.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    try:
        mctDriveSimulation = MCT_Drive_Simulation(logger);
        mctDriveSimulation.run();

    except KeyboardInterrupt:
        pass;

    mctDriveSimulation.stop();

    sys.exit(0);

## EOF.
