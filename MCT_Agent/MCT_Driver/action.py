#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
import ConfigParser;
import hashlib;
import time;
import ast;
import logging;

from nova.virt.mct.communication import MCT_Communication;
from nova.virt.mct.database      import MCT_Database;
from nova.virt.mct.utils         import *;




###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE = '/etc/mct/mct_drive.ini';

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
        self.__cfg = get_configs(CONFIG_FILE);

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = MCT_Database(self.__cfg['database']); 

        ## Communication object:
        self.__communication = MCT_Communication();


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
        idx = self.__cfg['main']['player'] + '_' + self.__create_index();

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(0, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__communication.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        dataReceived = self.__waiting_return(idx);

        ## LOG:
        LOG.info('[MCT_ACTION] DATA RECEIVED: %s', dataReceived);

        ## Return the all datas about resouces avaliable in player's division.
        return dataReceived;


    ##
    ## BRIEF: create a new instance via MCT.
    ## ------------------------------------------------------------------------
    ## @PARAM data == data received from MCT_Drive (OpenStack).
    ##
    def create_instance(self, data):

        ## LOG:
        LOG.info('[MCT_ACTION] CREATE - SEND REQUEST TO CREATE A NEW INSTANCE!');

        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = self.__cfg['main']['player'] + '_' + data['instance']['uuid'];

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(1, idx);

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
        valret = self.__communication.publish(msgToSend);

        if valret != -1:
            ## Waiting for the answer (looking the dbase) . The answer is ready
            ## when MCT_Agent send the return.
            dataReceived = self.__waiting_return(idx);
        else:
            dataReceived = {};

        ## LOG:
        LOG.info('[MCT_ACTION] CREATE - DATA RECEIVED: %s', dataReceived);

        ## Returns the status of the creation of the instance:
        return dataReceived;

 
    ##
    ## BRIEF: delete remote instance.
    ## ------------------------------------------------------------------------
    ## @PARAM uuid == vm instance uuid to be removed.
    ##
    def delete_instance(self, uuid):

        ## LOG:
        LOG.info('[MCT_ACTION] DELETE - SEND REQUEST TO DELETE AN INSTANCE!');

        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = self.__cfg['main']['player'] + '_' + str(uuid);

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(2, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__communication.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        dataReceived = self.__waiting_return(idx);

        ## LOG:
        LOG.info('[MCT_ACTION] DELETE - DATA RECEIVED: %s', dataReceived);

        ## Returns the status of the creation of the instance:
        return dataReceived;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM data == data received from MCT_Drive (OpenStack).
    ##
    def poweroff_instance(self, data):

        ## LOG:
        LOG.info('[MCT_ACTION] POWER OFF AN REMOTE INSTANCE!');

        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = data['instance']['uuid'];

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(3, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__communication.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        dataReceived = self.__waiting_return(idx);

        ## LOG:
        LOG.info('[MCT_ACTION] DATA RECEIVED: %s', dataReceived);

        ## Return the all datas about resouces avaliable in player's division.
        return dataReceived;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM data == data received from MCT_Drive (OpenStack).
    ##
    def poweron_instance(self, data):
        ## LOG:
        LOG.info('[MCT_ACTION] POWER OFF AN REMOTE INSTANCE!');


        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = data['instance']['uuid'];

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(4, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__communication.publish(msgToSend);

        ## Waiting for the answer is ready in database.The answer is ready when
        ## MCT_Agent send the return.
        dataReceived = self.__waiting_return(idx);

        ## LOG:
        LOG.info('[MCT_ACTION] DATA RECEIVED: %s', dataReceived);

        ## Return the all datas about resouces avaliable in player's division.
        return dataReceived;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM data == data received from MCT_Drive (OpenStack).
    ##
    def reset_instance(self, data):
        ## LOG:
        LOG.info('[MCT_ACTION] POWER OFF AN REMOTE INSTANCE!');


        ## Obtain the request identifier (use the "UUID" created by OpenStack).
        idx = data['instance']['uuid'];

        ## Create basic message to send to MCT_Agent. MCT_Agent is responsible
        ## to exec de action.
        msgToSend = self.__create_basic_message(5, idx);

        ## Send the request to the MCT_Action via asynchronous protocol (AMPQP).
        self.__communication.publish(msgToSend);

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

        count = int(self.__cfg['main']['request_pending_maxtries']);

        ## Waiting for the answer arrive. When the status change status get it.
        while True and count > 0:

            ## Mount the select query: 
            dbQuery  ="SELECT SQL_NO_CACHE status, message FROM REQUEST WHERE ";
            dbQuery +="request_id='" + requestId + "'";
 
            dataReceived = [] or self.__dbConnection.select_query(dbQuery);

            if dataReceived != []:
                ## LOG:
                LOG.info("DATA RECEIVED %s", dataReceived[0]);

                valRet = {
                    'status': dataReceived[0][0],
                    'data'  : ast.literal_eval(dataReceived[0][1])
                }

                return valRet;

            ## Wating for a predefined time to check (pooling) the list again.
            time.sleep(float(self.__cfg['main']['request_pending_timeout']));
            count -= 1;

            ## LOG:
            LOG.info("(%s) WAITING FOR REQUEST RETURN: %s", count, requestId);

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
            'playerId': self.__cfg['main']['player'],
            'status'  : 0,
            'reqId'   : index,
            'retId'   : '',
            'origAdd' : self.__cfg['main']['address_external'],
            'destAdd' : '',
            'data'    : {}
        };

        return message;
## EOF.
