#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
import ConfigParser;
import hashlib;
import time;
import ast;
import logging;

from nova.virt.mct.lib.communication import MCT_Communication;
from nova.virt.mct.lib.database      import MCT_Database;




###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE = '/etc/mct/mct_drive.ini';

## This is a dictionary of dictionary.Each position is a dictionary that repre-
## sent a request pendind to MCT_Agent via AMQP.
REQUEST_PENDING_TIMEOUT = 5;
REQUEST_PENDING_MAXTRY  = 50;

LOG = logging.getLogger(__name__)




###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Action(object):


    """
    Class MCT_Action: interface layer between MCT_Agent service and MCT_Drive.
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    ** get_resources_inf == get MCT resouces information.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    state           = None;
    data            = None;
    __communication = None;
    __dbConnection  = None;
    __cfg           = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, returnState):
        
        ## Power state is the state we get by calling virt driver on a particu-
        ## lar domain. The hypervisor is always considered the authority on the
        ## status of a particular VM and the power_state in the DB should be vi
        ## ewed as a snapshot of the VMs's state in the (recent) past.It can be
        ## periodically updated,and should also be updated at the end of a task
        ## if the task is supposed to affect power_state.
        self.__returnState = returnState;

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        self.__cfg = self.__get_config(CONFIG_FILE);

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = MCT_Database(self.__cfg['database']); 

        ## Instance the object that will communicate with MCT_Action.Running in
        ## thread.
        self.__communication = MCT_Communication(self.__dbConnection);
        self.__communication.daemon = True;
        self.__communication.start();


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
    ## BRIEF: create a new instance via MCT.
    ## ------------------------------------------------------------------------
    ## @PARAM data == data received from MCT_Drive (OpenStack).
    ##
    def create_instance(self, data):
        #flavor = data['instance']['instance_type_name'];

        ## Mount the requirement:
        data = {
            'vcpus' : data['instance']['vcpus'    ],
            'mem'   : data['instance']['memory_mb'],
            'disk'  : data['instance']['root_gb'  ],
            'name'  : data['instance']['name'     ],
            'uuid'  : data['instance']['uuid'     ],
            'image' : data['image'   ]['name'     ],
            'flavor': 'm1.tiny'
        };

        ## Protocol: [001] means create a new virtual machine in 'remote site'.
        dataToSend = {
            'opercode': '001',
            'data'    : data
        };

        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = data['instance']['uuid'];

        ## Insert the current request in the structure that represents the req-
        ## uests who are waiting for response.
        self.__insert_request_pending(idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__send_to_agent(dataToSend);

        ## Waiting for the answer arrive. When the status change from 'waiting'
        ## to 'ready' retrieves the return.
        while self.__requestPeding[idx]['status_request'] == 'waiting':
            time.sleep(REQUEST_PENDING_TIMEOUT);

        ## Obtain the data received from request. These data are related to the
        ## creation of an instance.
        dataReceived = self.__requestPeding[idx]['data']; 

        ## Remove the request received from the list of requests that are still
        ## pending.
        self.__remove_request_pending(idx);

        ## Returns the status of the creation of the instance:
        return self.__returnState[dataReceived['valret']];

 
    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def delete_instance(self, data):

        self.name  = data['instance']['name'     ];
        self.uuid  = data['instance']['uuid'     ];
        self.vcpus = data['instance']['vcpus'    ];
        self.mem   = data['instance']['memory_mb'];
        self.disk  = data['instance']['root_gb'  ];

        ##
        data = {
                     'vcpus' : self.vcpus,
                     'mem'   : self.mem,
                     'disk'  : self.disk,
                     'name'  : self.name,
                     'uuid'  : self.uuid,
               };

        ## Protocol: [002] delete a new virtual machine!
        dataToSend = {
                          "opercode": '002',
                          "data"    : data
                     };

        ##
        dataReceived = self.__send_to_agent(dataToSend);

        ##
        return self.__returnState[dataReceived['valret']];


    ##
    ## BRIEF: Get the resources from player's division.
    ## ------------------------------------------------------------------------
    ## TODO: verificar um numero de tentativas e caso nao consiga apos ele eh
    ##       porque nao conseguiu comunicar. Gerar erro e retornar dictionario
    ##       vazio.
    ##
    def get_resource_inf(self):

        ## LOG:
        LOG.info('[MCT_ACTION] GETTING MCT RESOURCE INFORMATION!');

        ## Create an idx to identify the request for the resources information.
        idx = self.__create_index();

        ## Protocol: [000] get player status!
        dataToSend = {
            'code'    : 0,
            'playerId': self.__cfg['main']['player'],
            'status'  : 0,
            'reqId'   : idx,
            'retId'   : '',
            'origAdd' : self.__cfg['main']['address'],
            'destAdd' : '',
            'data'    : {}
        };

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__send_to_agent(dataToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        dataReceived = self.__waiting_return(idx);

        ## LOG:
        LOG.info('[MCT_ACTION] DATA RECEIVED: %s', dataReceived);

        ## Return the all datas about resouces avaliable in player's division.
        return dataReceived;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: Waiting for the answer is ready in database.
    ## ------------------------------------------------------------------------
    ## @PARAM str requestId = identify of the resquest.
    ##
    def __waiting_return(self, requestId):
        count = 0;

        ## Waiting for the answer arrive. When the status change status get it.
        while True or count < REQUEST_PENDING_MAXTRY:

            ## Mount the select query: 
            dbQuery  = "SELECT message FROM REQUEST WHERE ";
            dbQuery += "request_id='" + requestId + "'";

            dataReceived = [] or self.__dbConnection.select_query(dbQuery);

            if dataReceived != []:
                ## LOG:
                LOG.info("[MCT_ACTION] DATA RECEIVED %s", dataReceived[0][0]);

                return ast.literal_eval(dataReceived[0][0]);

            ## Wating for a predefined time to check (pooling) the list again.
            time.sleep(REQUEST_PENDING_TIMEOUT);
            count += 1;

            ## LOG:
            LOG.info("[MCT_ACTION] WAITING FOR RETURN FROM s", dataReceived);

        return {};        


    ##
    ## BRIEF: send the message to MCT_Agent.
    ## ------------------------------------------------------------------------
    ## @PARAM message == message to send.
    ##
    def __send_to_agent(self, message):

        self.__communication.publish(message);
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
    ## BRIEF: obtain all configuration from conffiles.
    ## ------------------------------------------------------------------------
    ## @PARAM str cfgFile == conffile name.
    ##
    def __get_config(self, cfgFile):
       cfg = {};

       config = ConfigParser.ConfigParser();
       config.readfp(open(cfgFile));

       for section in config.sections():
           cfg[section] = {};

           for option in config.options(section):
               cfg[section][option] = config.get(section, option);

       return cfg;
## EOF.
