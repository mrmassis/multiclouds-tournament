#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
import ConfigParser;
import hashlib;
import time;
import ast;
import logging;
import logging.handlers;
import sys;

from multiprocessing   import Process, Queue, Lock;
from mct.lib.database  import MCT_Database;
from mct.lib.utils     import *;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE   = 'mct_emulator.ini';
LOG_NAME      = 'MCT_Emulator';
LOG_FORMAT    = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s';
LOG_FILENAME  = '/var/log/mct/mct_emulator.log';








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


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, cfg):

        ## LOG:
        LOG.info('[MCT_COMMUNICATION] INITIALIZE COMMUNICATION OBJECT!');

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
        LOG.info('[MCT_COMMUNICATION] PUBLISH MESSAGE: %s', message);

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
## EOF.




class MCT_Action(object):

    """
    Class MCT_Action: interface layer between MCT_Agent service and MCT_Drive.
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    ** get_resources_inf == get MCT resouces information.
    ** create_instance   ==
    ** delete_instance   ==
    ** poweroff_instance ==
    ** poweron_instance  ==
    ** reset_instance    ==
    """


    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    state           = None;
    data            = None;
    __dbConnection  = None;
    __cfgAgent      = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, config):
        
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
            'queue'     : config['amqp_queue_name']
        }

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__publish = MCT_Simple_AMQP_Publish(amqpConfig);

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = MCT_Database(self.__cfgAgent['database']); 


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
    ## @PARAM code == the action to do.
    ## @PARAM data == payload to send.
    ##
    def dispatch(self, code, data):

       ## Get resouces information from mct_referee. 
       if   code == 'GET_INF':
           get_resource_info();

       ## Set resources information to  mct_referee.
       elif code == 'SET_INF':
           get_resource_info();

       ## Create a 'virtual' server in remote hosts.
       elif code == 'ADD_VMS':
           create_instance(data);

       ## Delete a 'virtual' server in remote hosts.
       elif code == 'DEL_VMS':
           delete_instance(data);
 

    ##
    ## BRIEF: Get the resources from player's division.
    ## ------------------------------------------------------------------------
    ##
    def get_resource_inf(self):

        ## LOG:
        logger.info('[MCT_ACTION] GETTING MCT RESOURCE INFORMATION!');

        ## Create an idx to identify the request for the resources information.
        idx = self.__vplayerName + '_' + self.__create_index();

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(GETINF_RESOURCE, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        dataReceived = self.__waiting_return(self.__vplayerName, idx);

        ## LOG:
        logger.info('[MCT_ACTION] DATA RECEIVED: %s', dataReceived);

        ## Return the all datas about resouces avaliable in player's division.
        return dataReceived;


    ##
    ## BRIEF: create a new instance via MCT.
    ## ------------------------------------------------------------------------
    ## @PARAM data == data received from MCT_Drive (OpenStack).
    ##
    def create_instance(self, data):

        ## LOG:
        logger.info('[MCT_ACTION] CREATE - SEND REQUEST TO CREATE A NEW INSTANCE!');

        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = self.__vplayerName + '_' + data['instance']['uuid'];

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(CREATE_INSTANCE, idx);

        ## Mount the requirement:
        data = {
            'vcpus' : data['instance']['vcpus'       ],
            'mem'   : data['instance']['memory_mb'   ],
            'disk'  : data['instance']['root_gb'     ],
            'name'  : data['instance']['display_name'],
            'uuid'  : data['instance']['uuid'        ],
            'image' : data['image'   ]['name'        ]
        };

        msgToSend['data'] = data;

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        valret = self.__publish.publish(msgToSend);

        if valret != -1:
            ## Waiting for the answer (looking the dbase) . The answer is ready
            ## when MCT_Agent send the return.
            dataReceived = self.__waiting_return(self.__vplayerName, idx);
        else:
            dataReceived = {};

        ## LOG:
        logger.info('[MCT_ACTION] CREATE - DATA RECEIVED: %s', dataReceived);

        ## Returns the status of the creation of the instance:
        return dataReceived;

 
    ##
    ## BRIEF: delete remote instance.
    ## ------------------------------------------------------------------------
    ## @PARAM data == data received from MCT_Drive (OpenStack).
    ##
    def delete_instance(self, data):

        ## LOG:
        logger.info('[MCT_ACTION] DELETE - SEND REQUEST TO DELETE AN INSTANCE!');

        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = self.__vplayerName + '_' + data['instance']['uuid'];

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(DELETE_INSTANCE, idx);

        data = {
            'vcpus' : data['instance']['vcpus'       ],
            'mem'   : data['instance']['memory_mb'   ],
            'disk'  : data['instance']['root_gb'     ]
        };

        msgToSend['data'] = data;

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__publish.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        dataReceived = self.__waiting_return(self.__vplayerName, idx);

        ## LOG:
        logger.info('[MCT_ACTION] DELETE - DATA RECEIVED: %s', dataReceived);

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
 
            dataReceived = [] or self.__dbConnection.select_query(dbQuery);

            if dataReceived != []:
                ## LOG:
                logger.info("DATA RECEIVED %s", dataReceived[0]);

                valRet = {
                    'status': dataReceived[0][0],
                    'data'  : ast.literal_eval(dataReceived[0][1])
                }

                return valRet;

            ## Wating for a predefined time to check (pooling) the list again.
            time.sleep(self.__requestPendingWaiting);
            count += 1;

            ## LOG:
            logger.info("(%s) WAITING FOR REQUEST RETURN: %s", count, requestId);

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
            'origAdd' : self.__cfgAgent['my_ip'],
            'destAdd' : '',
            'data'    : {}
        };

        return message;
## END CLASS.




class MCT_VPlayer(Process):

    '''
    Class MCT_Emulation: emulation the player.
    ---------------------------------------------------------------------------
     
    '''

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __mctAction = None;
    __mctStates = None;
    __states    = None;
 

    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM playerCfg == configuration file.
    ##
    def __init__(self, playerCfg):
        super(MCT_Emulation, self).__init__();

        ## Object that send actions to the MCT_Agent and other that generates
        ## state to exec.
        self.__mctAction = MCT_Action(playerCfg);
        self.__mctStates = MCT_States();
        
        self.__states = self.__load_states(playerCfg['states']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):
 
        ## Initialized the pool states:
        self.__mctStates.init_pool(self.__states);

        while True:
            ## Obtain one state select from the 'pool' of the possible states:
            state = self.__mctStates.give_me_state_from_pool();

            data = {};
      
            self.__mctAction.dispatch(state, data);
            time.sleep(5);
 
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: transform string states in list of states..
    ## ------------------------------------------------------------------------
    ## @PARAM states == possibles states.
    ##
    def __load_states(self, states):
        ## Split the string in pieces (list of the states).
        statesList = states.split(' ');

        return statesList;


    ##
    ## BRIEF: mount data to send.
    ## ------------------------------------------------------------------------
    ##
    def __mount_data(self):
        data = {
            'vcpus' : '',
            'mem'   : '',
            'disk'  : '',
            'name'  : '',
            'uuid'  : '',
            'image' : ''
        }

        return data;
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


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: initialized the pool of the states.
    ## ------------------------------------------------------------------------
    ## @PARAM states   = list of the possibles states.
    ## @PARAM poolName = name of pool.
    ##
    def init_pool(self, states, poolName='default'):
        self.__pools[poolName] = states;
        return 0;


    ##
    ## BRIEF: return one state (in str) from a pool.
    ## ------------------------------------------------------------------------
    ## @PARAM poolName = name of pool.
    ##
    def give_me_state_from_pool(poolName='default'):
       return 'GETINF_RESOURCE';

## END CLASS.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    ## LOG:
    logger.info('EXECUTION STARTED...');

    try:
        vPlayers = [];

        ## Get from configuration file all players and all respective paramters
        vPlayersCfg = get_configs(CONFIG_FILE);

        ## To each player run in thread a simulation:
        for i in range(int(vPlayersCfg['main']['vplayers'])):
            vPlayers.append(MCT_VPlayer(vPlayersCfg['vplayer' + str(i)]));
            vPlayers[i].name   = 'vplayers' + str(i);
            vPlayers[i].daemon = True;
            vPlayers[i].start();
            
            ## Wait the unpredicable time. 
            mutable_time_to_waiting(0.3, 5.0);

        while True:
             time.sleep(5);

    except KeyboardInterrupt:
        for vPlayer in vPlayers:
            vPlayer.terminate();
            vPlayer.join();

    ## LOG:
    logger.info('EXECUTION FINISHED...');
    sys.exit(0);
## EOF.
