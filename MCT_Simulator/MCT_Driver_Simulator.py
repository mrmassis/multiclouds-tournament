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

from threading         import Timer;
from multiprocessing   import Process, Queue, Lock;
from mct.lib.database  import MCT_Database;
from mct.lib.utils     import *;








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
#logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)

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
## FUNCTION                                                                  ##
###############################################################################
##
## BRIEF: mantain the virtual player state.
## ----------------------------------------------------------------------------
## @PARAM vPlayerName  == virtual player name.
## @PARAM dbConnection == database connection.
##
##
def get_virtual_player_state(vPlayerName, dbConnection):
     stateDictionary = {
         'vPlayer': vPlayerName,
         'vmsRcv' : [],
         'vmsSnd' : []
     };

     ## Perform a select to get all vm instances assign (running) in 'vPlayer'.
     ## ----
     dbQuery  = "SELECT vm_id,vm_owner,vm_type FROM STATE WHERE ";
     dbQuery += "player_id='" + vPlayerName + "' and running='1'";

     dataReceived = [] or dbConnection['connection'].select_query(dbQuery);

     if dataReceived != []:
         for vm in dataReceived:
             if vm[1] == vPlayerName:
                 stateDictionary['vmsRcv'].append(vm);
             else:
                 stateDictionary['vmsSnd'].append(vm);

     return stateDictionary;








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

        except (AMQPConnectionError, AMQPChannelError), error:
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
    ## @PARAM config       == configuration dictionary.
    ## @PARAM dbConnection == connection with database.
    ## @PARAM logger       == log object.
    ##
    def __init__(self, config, dbConnection, logger):
        
        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(config['print'], logger);

        ## Get which route is used to deliver the msg to the 'correct destine'.
        self.__route = config['amqp_route'];

        ## Get player identifier:
        self.__vplayerName = config['name'];

        ## Iteraction number and time to wainting response between iteractions.
        self.__requestPendingWaiting = float(config['request_pending_waiting']);
        self.__requestPendingIteract =   int(config['request_pending_iteract']);

        amqpConfig = {
            'user'      : config['amqp_user'      ],
            'pass'      : config['amqp_pass'      ],
            'route'     : config['amqp_route'     ],
            'identifier': config['amqp_identifier'],
            'address'   : config['amqp_address'   ],
            'exchange'  : config['amqp_exchange'  ],
            'queue'     : config['amqp_queue_name'],
            'print'     : config['print'          ]
        }

        ##
        self.__myIp = config['agent_address'];

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish = MCT_Simple_AMQP_Publish(amqpConfig, logger);

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = dbConnection;


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
    ## @PARAM data == dictionary with data to dispatch.
    ##
    def dispatch(self, data):
       dataReceived = {};

       ## Get resouces information from mct_referee. 
       if   data['action'] == GETINF_RESOURCE:
           dataReceived = self.getinf_resource();

       ## Set resources information to  mct_referee.
       elif data['action'] == SETINF_RESOURCE:
           dataReceived = self.setinf_resource(data);

       ## Create a 'virtual' server in remote hosts.
       elif data['action'] == CREATE_INSTANCE:
           dataReceived = self.create_instance(data);

       ## Delete a 'virtual' server in remote hosts.
       elif data['action'] == DELETE_INSTANCE:
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
        idx = self.__vplayerName + '_' + self.__create_index();

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(GETINF_RESOURCE, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dataReceived = self.__waiting_return(self.__vplayerName, idx);
        else:
            dataReceived = {};

        ## LOG:
        self.__print.show('|GETINF| - data received: '+str(dataReceived), 'I');

        ## Return the all datas about resouces avaliable in player's division.
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
        idx = self.__vplayerName + '_' + self.__create_index();

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(SETINF_RESOURCE, idx);

        vmData = {
            'vcpus' : data['vcpus' ],
            'memory': data['memory'],
            'disk'  : data['disk'  ]
        }

        msgToSend['data'] = vmData;

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dataReceived = self.__waiting_return(self.__vplayerName, idx);
        else:
            dataReceived = {};

        ## LOG:
        self.__print.show('|SETINF| - data received: '+str(dataReceived), 'I');

        ## Return the all datas about resouces avaliable in player's division.
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
        idx = self.__vplayerName + '_' + str(data['machineID']);

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(CREATE_INSTANCE, idx);

        vmData = {
           'name'  : idx,
           'uuid'  : idx,
           'flavor': FLV_NAME[data['vmType']],
           'vcpus' : CPU_INFO[data['vmType']],
           'mem'   : MEM_INFO[data['vmType']],
           'disk'  : DSK_INFO[data['vmType']],
           'image' : IMG_NAME,
           'net'   : NET_NAME 
        }

        msgToSend['data'] = vmData;

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dataReceived = self.__waiting_return(self.__vplayerName, idx);
        else:
            dataReceived = {};

        ## LOG:
        self.__print.show('|CREATE| - data received: '+str(dataReceived), 'I');

        ## Returns the status of the creation of the instance:
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
        idx = self.__vplayerName + '_' + str(data['machineID']);

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(DELETE_INSTANCE, idx);

        vmData = {
           'name'  : idx,
           'uuid'  : idx
        }

        msgToSend['data'] = vmData;

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dataReceived = self.__waiting_return(self.__vplayerName, idx);
        else:
            dataReceived = {};

        ## LOG:
        self.__print.show('|DELETE| - data received: '+str(dataReceived), 'I');

        ## Returns the status of the creation of the instance:
        return dataReceived;


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

            ## Mount the select query: 
            dbQuery  ="SELECT SQL_NO_CACHE status, message FROM REQUEST WHERE ";
            dbQuery +="player_id='"  + playerId  + "' and ";
            dbQuery +="request_id='" + requestId + "'";
 
            with self.__dbConnection['lock']:
                dataReceived = [] or \
                self.__dbConnection['connection'].select_query(dbQuery);

            ## If there is return finish the process!
            if dataReceived != []:

                ## LOG:
                #self.__print.show('DATA RECEIVED: '+str(dataReceived[0]), 'I');

                valRet = {
                    'status': dataReceived[0][0],
                    'data'  : ast.literal_eval(dataReceived[0][1])
                }

                return valRet;

            ## Wating for a predefined time to check (pooling) the list again.
            time.sleep(self.__requestPendingWaiting);
            count += 1;

            ## LOG:
            self.__print.show('WAITING FOR REQUEST RETURN: ' + requestId, 'I');

        return {};        


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
            'playerId': self.__vplayerName,
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
    ## @PARAM config == virtual player configuration.
    ## @PARAM logger == log object.
    ##
    def __init__(self, config, logger):
  
       ## Get the option that define to where the logs will are sent to show.
       self.__print = Show_Actions(config['print'], logger);

       self.__vcpus  = config['vcpus' ];
       self.__memory = config['memory'];
       self.__disk   = config['disk'  ];
       self.__addr   = config['addr'  ];
       self.__port   = config['port'  ];

       self.__messageDictSend = {
           'authentication' : '',
           'action'         : '',
           'player'         : config['name']
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

            ## Load the JSON message. Convert from JSON format to simple dicti-
            ## onary.
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
    __playerName              = None;
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
 

    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM playerCfg == configuration file.
    ## @PARAM db        == connection with database.
    ## @PARAM logger    == log object.
    ##
    def __init__(self, playerCfg, playerState, db, logger):
        super(MCT_VPlayer, self).__init__();

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(playerCfg['print'], logger);

        ## Player name:
        self.__playerName = playerCfg['name'];

        ## LOG:
        self.__print.show('INITIALIZE VPLAYER: ' + self.__playerName, 'I');

        ## Set the objet that represent the connection with database (is neces-
        ## sary to use the lock object).
        self.__db = db;

        ## Object that send actions to the MCT_Agent and other that generates
        ## state to exec.
        self.__mctAction = MCT_Action(playerCfg, self.__db, logger);
        self.__mctStates = MCT_States(playerCfg, logger);

        ## Time to send get resource info and set resources info request to MCT
        ## referee:
        self.__interval = float(playerCfg['get_set_resources_info_time']);

        ## Resource: 
        self.__vcpu = int(playerCfg['vcpus' ]);
        self.__disk = int(playerCfg['disk'  ]);
        self.__memo = int(playerCfg['memory']);

        ## Init the avaliable resources database:
        self.__init_avaliable_resources();


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):
        oldTime = 0;

        ## Scheduller set and get information to/from MCT main components.
        getSetInfRepeat = Repeated_Timer(self.__interval, self.__get_set_info);

        while True:

            ## Get a new action from database through the MCT_DB_Proxy service.
            message = self.__mctStates.give_me_state_from_database();
      
            if message['valid'] != 2:

                if   message['action'] == 0:
                     message['action'] = CREATE_INSTANCE;

                elif message['action'] == 1:
                     message['action'] = DELETE_INSTANCE;

                ## Calculate the new time to waiting until perform new action.
                newTime = float(message['time']/(N_VALUE*N_FACTOR)) - oldTime; 
                oldTime = newTime;

                if newTime < 1.0:
                    newTime = 1;

                ## Wait X seconds to dispatich a new action to the 'MCT_Agent'.
                time.sleep(float(newTime));
                   
                ## Dispatch the action to MCT_Dispatch:
                dataRecv = self.__mctAction.dispatch(message);

                ## Update the database with the status from action (create/dele
                ## te instances).
                self.__update_database(message, dataRecv);

            ## Obtain one state select from the 'pool' of the possible states:
            else:
                getSetInfRepeat.stop();
                break;

        ## LOG:
        self.__print.show('END SIMULATION PLAYER: ' + self.__playerName, 'I');
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: set initial avaliable resources to vplayer.
    ## ------------------------------------------------------------------------
    ##
    def __init_avaliable_resources(self):

        ## In the first time, create a new user in the respective table. When
        ## the player already exist, only update then.
        query  = "INSERT INTO AVALIABLE_RESOURCES "  ;
        query += "(player_id,vcpus,memory,local_gb) ";
        query += "VALUES (%s,%s,%s,%s)";
        value  = (str(self.__playerName),
                  str(self.__vcpu),
                  int(self.__memo),
                  str(self.__disk));

        with self.__db['lock']:
            try:
                valRet = self.__db['connection'].insert_query(query,value);

                ## LOG:
                self.__print.show('INSERT RESOURCE VALUES IN TABLE!', 'I');
                return 0;
            except mysql.connector.Error as mysqlError:
                ## LOG:
                self.__print.show('MYSQL ERROR: ' + str(mysqlError), 'E');

        ## 
        query  = "UPDATE AVALIABLE_RESOURCES SET "
        query += "vcpus='"           + str(self.__vcpu)        + "',";
        query += "memory='"          + str(self.__memo)        + "',";
        query += "local_gb='"        + str(self.__disk)        + "' ";
        query += "WHERE player_id='" + str(self.__playerName)  + "'" ;
 
        with self.__db['lock']:
            try:
                 valRet = self.__db['connection'].update_query(query);

                 ## LOG:
                 self.__print.show('UPDATE RESOURCE VALUES IN TABLE!','I');
                 return 0;
            except mysql.connector.Error as err:
                 ## LOG:
                 self.__print.show('MYSQL ERROR: ' + mysqlError, 'E');

        return 1;


    ##
    ## BRIEF: update database with status from action (create/delete instances)
    ## ------------------------------------------------------------------------
    ## @PARAM message  == message to publish.
    ## @PARAM dataRecv == message response.
    ##
    def __update_database(self, message, dataRecv):
        ## self.__dbConnection:
        pass


    ##
    ## BRIEF: send request to get and set information.
    ## ------------------------------------------------------------------------
    ##
    def __get_set_info(self):

        ## Check the last action. If was get execute the set information, other
        ## wise execute the get. 
        if self.__get == True:
            
            message = {
                'action' : GETINF_RESOURCE
            }

        else:
            
            message = {
                'action': SETINF_RESOURCE,
                'vcpus' : self.__vcpu,
                'memory': self.__memo,
                'disk'  : self.__disk
            }

        ## Select the next action: 'True' to 'False', 'Get to Set' information.
        self.__get = not self.__get;

        ## Dispatch the action to MCT_Dispatch:
        dataRecv = self.__mctAction.dispatch(message);

## END CLASS.








class MCT_Drive_Simulation:
    """
    Class MCT_Drive_Simulation: main class in the module.
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __vPlayers = [];
    __db       = {};
    __cfg      = None;
    __print    = None;


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

        ## Launch all player defined in configfile. Executing then in threads.
        self.__launch_vplayers();


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: excute the MCT_Drive_Simulation.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        ## Check if the threads (vPlayers) is already running:
        while self.__vPlayers != []:
             auxList = [];
             for vPlayer in self.__vPlayers:
                 if vPlayer.is_alive():
                     auxList.append(vPlayer);

             self.__vPlayers = auxList;
             time.sleep(5);


    ##
    ## BRIEF: stop the execution.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        ## Stop all virtual player executing in thread:
        for vPlayer in self.__vPlayers:
            vPlayer.terminate();
            vPlayer.join();


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

        try:
           ## Connect to database (use the crendetiais defined in the cfg file):
           self.__db['connection'] = MCT_Database(self.__cfg['database']);

           ## A primitive lock is a synchronization primitive that is not owned
           ## by a particular thread when locked.
           self.__db['lock'] = Lock();

        except mysql.connector.Error as mysqlError: 

            if   mysqlError.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                messageError = '|DB|] SOMETHING IS WRONG WITH USER/PASS!';

            elif mysqlError.errno == errorcode.ER_BAD_DB_ERROR:
                messageError = '[DB] DATABASE DOES NOT EXIST!';

            else:
                messageError = '|DB| ' + str(mysqError);

            ## LOG:
            self.__print(messageError, 'E');
            sys.exit(1);


    ##
    ## BRIEF: launch the vplayers.
    ## ------------------------------------------------------------------------
    ##
    def __launch_vplayers(self):

        ## To each player run in thread a simulation:
        for i in range(int(self.__cfg['main']['vplayers'])):

            ## Get configuration options to the virtual player (amqp cfg, etc).
            vCfg = self.__cfg['vplayer' + str(i)];

            ## Get the actual virtual player state stored in database.
            ## ----------------------------------------------------------------
            vState = get_virtual_player_state(vCfg['name'], self.__db);

            ## Running vplayers in the threads:
            self.__vPlayers.append(MCT_VPlayer(vCfg,vState,self.__db,logger));
            self.__vPlayers[i].daemon = True;
            self.__vPlayers[i].start();

            ## Wait the unpredicable time. 
            mutable_time_to_waiting(0.3, 5.0);

## END CLASS.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    try:
         mctDriveSimulation = MCT_Drive_Simulation(logger);
         mctDriveSimulation.run();

    except KeyboardInterrupt:
         mctDriveSimulation.stop();

    sys.exit(0);

## EOF.
