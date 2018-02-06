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
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy, Request;
from mct.lib.utils               import *;
from mct.lib.amqp                import MCT_Simple_AMQP_Publish;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE           = 'mct-simulation.ini';
HOME_FOLDER           = os.path.join(os.environ['HOME'], CONFIG_FILE);
RUNNING_FOLDER        = os.path.join('./'              , CONFIG_FILE);
DEFAULT_CONFIG_FOLDER = os.path.join('/etc/mct/'       , CONFIG_FILE);








###############################################################################
## LOG                                                                       ##
###############################################################################
#logging.basicConfig()







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
    state                   = None;
    data                    = None;
    __agentId               = None;
    __db                    = None;
    __name                  = None;
    __myIp                  = None;
    __print                 = None;
    __route                 = None;
    __requestPendingWaiting = None;
    __requestPendingIteract = None;
    __runningVM             = {};


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

        ## Get player credentials (Name, IP, and ID):
        self.__name    = vCfg['name'];
        self.__myIp    = vCfg['agent_address'];
        self.__agentId = vCfg['agent_id'];

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
    def dispatch(self, action, data={}):
       dRecv = {};

       ## Perform the new player register in MCT_Register. Get an access token.
       if   action == ADD_REG_PLAYER:
           dRecv = self.addreg_vplayer(data);

       ## Unregister the existent player from tournament. Put the player in sus
       ## pense mode.
       elif action == SUS_REG_PLAYER:
           dRecv = self.delreg_vplayer(data);

       ## Get resouces information from MCT_Referee. 
       if   action == GETINF_RESOURCE:
           dRecv = self.getinf_resource(data);

       ## Set resources information to  MCT_Referee.
       elif action == SETINF_RESOURCE:
           dRecv = self.setinf_resource(data);

       ## Create a 'virtual' server in remote hosts.
       elif action == CREATE_INSTANCE:
           dRecv = self.create_instance(data);

       ## Delete a 'virtual' server in remote hosts.
       elif action == DELETE_INSTANCE:
           dRecv = self.delete_instance(data);

       ## Stop the vms executing by virtual player.
       elif action == STOPVM_INSTANCE:
           dRecv = self.stopvm_instance(data);

       return dRecv;


    ##
    ## BRIEF: Get the resources from player's division.
    ## ------------------------------------------------------------------------
    ## @PARAM data == specific data to send.
    ##
    def getinf_resource(self, data):

        ## LOG:
        self.__print.show('GETTING MCT RESOURCE INFORMATION!', 'I');

        ## Create an idx to identify the request for the resources information.
        idx = self.__name + '_' + self.__create_index();

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(GETINF_RESOURCE, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend, 'Agent_Drive');

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dRecv = self.__waiting_return(self.__name, idx);
        else:
            dRecv = {};

        ## LOG:
        self.__print.show('|GETINF| - data received: ' + str(dRecv), 'I');

        ## Return the data:
        return dRecv;


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
            'vcpus'       : data['vcpus'       ],
            'memory'      : data['memory'      ],
            'local_gb'    : data['local_gb'    ],
            'max_instance': data['max_instance'],
            'strategy'    : data['strategy'    ],
            'coalition'   : data['coalition'   ]
        }

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend, 'Agent_Drive');

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dRecv = self.__waiting_return(self.__name, idx);
        else:
            dRecv = {};

        ## LOG:
        self.__print.show('|SETINF| - data received: ' + str(dRecv), 'I');

        ## Return the data:
        return dRecv;


    ##
    ## BRIEF: stop all vms that this vplayer is running.
    ## ------------------------------------------------------------------------
    ## @PARAM data == specific data to send.
    ##
    def stopvm_instance(self, data):

        ## LOG:
        self.__print.show('SEND REQUEST TO STOP ALL VMS INSTANCE!', 'I');

        ## Create an idx to identify the request for the resources information.
        idx = self.__name + '_' + self.__create_index();

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(STOPVM_INSTANCE, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend, 'Agent_Drive');

        ## LOG:
        self.__print.show('|STOPVM|', 'I');

        ## Returns the data:
        return {};


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
        valret = self.__publish.publish(msgToSend, 'Agent_Drive');

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dRecv = self.__waiting_return(self.__name, idx);
        else:
            dRecv = {};

        ## LOG:
        self.__print.show('|CREATE| - data received: ' + str(dRecv), 'I');

        ## VM CONTROL ------------------------------------------------------ ##
        ## If status is sucessfull put vm running in vm structure:           ##
        ## ----------------------------------------------------------------- ##
        try:
            if int(dRecv['status']) == SUCCESS:
                self.__runningVM[dRecv['data']['uuid']] = 1;
        except:
             pass; 

        ## Returns the data:
        return dRecv;

 
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

        ## VM CONTROL ------------------------------------------------------ ##
        ## If VM exist is possible delete it.                                ##
        ## ----------------------------------------------------------------- ##
        if idx in self.__runningVM:
            del self.__runningVM[idx];

            ## Create basic message to send to MCT_Agent. MCT_Agent is respon-
            ## sible to exec de action.
            msgToSend = self.__create_basic_message(DELETE_INSTANCE, idx);

            msgToSend['data'] = {
                'name'  : idx,
                'uuid'  : idx
            };

            ## Send the request to the MCT_Action by asynchronous protocol AMPQ.
            valret = self.__publish.publish(msgToSend, 'Agent_Drive');

            ## Waiting for the answer is ready in database. The answer is ready
            ## when MCT_Agent send the return.
            if valret != -1:
                dRecv = self.__waiting_return(self.__name, idx);
            else:
                dRecv = {};

            ## LOG:
            self.__print.show('|DELETE| - data received: ' + str(dRecv), 'I');
        else:
            ## LOG:
            self.__print.show('|DELETE| - VM isnt running impossible DEL','I');
            dRecv = {};

        ## Returns the data:
        return dRecv;


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
        valret = self.__publish.publish(msgToSend, 'Agent_Drive');

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        if valret != -1:
            dRecv = self.__waiting_return(self.__name, idx);
        else:
            dRecv = {};

        ## LOG:
        self.__print.show('|REGISTER| - data received: ' + str(dRecv), 'I');

        ## Returns the data:
        return dRecv;
 

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

            if int(mDictRecv['valid']) == 2:
                sock.close();

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
    __ratio                   = None;
    __fairness                = 0.0;
    __id                      = None;
    __strategy                = None;


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

        ## Player name, id and address:
        self.__name = vCfg['name'];
        self.__id   = vCfg['id'  ];
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

        ## Value used to determined the time to waiting until the next action.
        self.__ratio = int(vCfg['ratio']);



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
        getSetInfRepeat= Repeated_Timer(self.__interval, self.__get_set_info);

        while True:

            ## Get a new action from database through the MCT_DB_Proxy service.
            data = self.__mctStates.give_me_state_from_database();
 

            print data['valid'];


            if int(data['valid']) != 2:

                ## Calculate the new time to waiting until perform "new action".
                newTime = float(data['time'] / (self.__ratio)) - oldTime;
                oldTime = newTime;

                if newTime < 1.0:
                    newTime = 1;

                ## Wait nTime seconds to dispatch a new action to the MCT_Agent.
                time.sleep(float(newTime));

                ## Dispatch the action to MCT_Dispatch:
                dRecv = self.__mctAction.dispatch(data['action'], data);

                ## Check if the virtual player is enabled to execute actions in
                ## tournament.
                try:
                    if int(dRecv['status']) == PLAYER_REMOVED:
                        ## LOG:
                        self.__print.show('REMOVED: ' + self.__name, 'I');

                        self.__remove_player_files();
                        getSetInfRepeat.stop();
                        return 0;

                except:
                    pass;
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
        dRecv = self.__mctAction.dispatch(GETINF_RESOURCE, {});

        ## Obtain the individual fairness:
        try:
            self.__fairness = float(dRecv['data']['fairness']);
        except:
            pass;


    ##
    ## BRIEF: set vplayer information to the tournament.
    ## ------------------------------------------------------------------------
    ##
    def __set_resources_info(self):
        ## Obtain the dictionary with resource informations (vcpus ,mem, disk).
        try:
            rDict = yaml.load(file(self.__resourcesFile, 'r')); 

            data = {
                'vcpus'        : rDict['vcpus'       ],
                'memory'       : rDict['memory'      ],
                'local_gb'     : rDict['local_gb'    ],
                'max_instance' : rDict['max_instance'],
                'strategy'     : rDict['strategy'    ]
            };

            ## Send the request to update 'resources' values to 'MCT_Dispatch':
            dRecv = self.__mctAction.dispatch(SETINF_RESOURCE, data);
            return SUCCESS;

        except yaml.reader.ReaderError:
            pass;

        return FAILED;


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

        return token;


    ##
    ## BRIEF: register virtual player.
    ## ------------------------------------------------------------------------ 
    ##
    def __delreg_me(self):
        ## Send the request:
        dRecv = self.__mctAction.dispatch(DELREG_PLAYER, {});

        return dRecv;

    ##
    ## BRIEF: remove player files.
    ## ------------------------------------------------------------------------
    ##
    def __remove_player_files(self):
        ## LOG:
        self.__print.show('REMOVE THE PLAYER: ' + str(self.__id), 'I');

        qFile = os.path.join('/etc/mct/quotas'  , 'resources' + str(self.__id) + '.yml');
        pFile = os.path.join('/etc/mct/vplayers', 'vplayer'   + str(self.__id) + '.yml');

        ## Remove all files:
        os.remove(qFile);
        os.remove(pFile);

        return SUCCESS;
## END CLASS.








class Main:

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
    __logger             = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ##
    def __init__(self):
   
        ## Get the configurantion parameters.
        self.__cfg = self.__get_configs();

        ## Configurate the logger. Use the parameters defineds in configuration
        ## file.
        self.__logger = self.__logger_setting(self.__cfg['log_drive']);

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(self.__cfg['main']['print'], self.__logger);

        ## Connect to database.
        self.__get_database();

        ## Obtain configuration options to the virtual player (amqp cfg, etc).
        self.__virtualPlayersPath = self.__cfg['vplayers']['dir'];


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: start the MCT_Drive_Simulation.
    ## ------------------------------------------------------------------------
    ##
    def start(self):

        ## LOG:
        self.__print.show("\n####### START MCT_DRIVE_SIMULATION #######\n",'I');

        while True:

            for vPlayer in os.listdir(self.__virtualPlayersPath):

                try:
                    ## Open virtual player config:
                    vCfg = yaml.load(file('/etc/mct/vplayers/' + vPlayer, 'r'));
                except:
                    continue;

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
 
        if vCfg['name'] in self.__vRunning:
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
        self.__vRunning[vCfg['name']]=MCT_VPlayer(vCfg,self.__db,self.__logger);
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
