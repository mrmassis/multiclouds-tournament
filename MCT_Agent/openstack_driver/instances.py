#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
import ConfigParser;

from nova.openstack.common import log as logging
from mct.lib.database      import MCT_Database;
from mct.lib.utils         import *;








###############################################################################
## DEFINITION                                                                ##
###############################################################################
CONFIG_FILE = '/etc/mct/mct-drive.ini';

LOG = logging.getLogger(__name__)








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Instances(object):

    """
    Class Instance: 
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __cfg          = None;
    __dbConnection = None;
    instanceDict   = {};
    ## TODO: remove!!!!
    max_mem        = 0;
    mem            = 0;
    num_cpu        = 2;
    cpu_time       = 0;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        self.__cfg = get_configs(CONFIG_FILE);

        ## Intance a new object to handler all operation in the local database.
        self.__dbConnection = MCT_Database(self.__cfg['database']);


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM key ==
    ##
    def __getitem__(self, key):
        return getattr(self, key);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: recovery all instances.
    ## ------------------------------------------------------------------------
    ##
    def recovery_instances(self):

        ## Select query:
        dbQuery = "SELECT * FROM INSTANCES"

        dataReceived = [] or self.__dbConnection.select_query(dbQuery);

        if dataReceived != []:

            for instance in dataReceived:
                self.instanceDict[instance[0]] = {
                    'name' : instance[1],
                    'vcpu' : instance[2],
                    'memo' : instance[3],
                    'disk' : instance[4],
                    'mcts' : instance[5],
                    'pwrs' : instance[6]
                };

        return 0;


    ##
    ## BRIEF: check if the uuid exist.
    ## ------------------------------------------------------------------------
    ## @PARAM uuid = uuid from instance.
    ##
    def check_exist(self, uuid):
        if uuid not in self.instanceDict:
            return False;

        return True;


    ##
    ## BRIEF: get the name of all instances.
    ## ------------------------------------------------------------------------
    ##
    def get_instances_name(self):
        instancesNameList = [];

        for uuid in self.instanceDict.keys():
            instancesNameList.append(self.instanceDict[uuid]['name']);

        return instancesNameList;


    ##
    ## BRIEF: get the uuid of all instances.
    ## ------------------------------------------------------------------------
    ##
    def get_instances_uuid(self):
        instancesUuidList = self.instanceDict.keys();
        return instancesUuidList;


    ##
    ## BRIEF: insert a new instance in the dictionary.
    ## ------------------------------------------------------------------------
    ## @PARAM instance ==
    ## @PARAM mctState ==
    ## @PARAM pwrState ==
    ##
    def insert(self, instance, mctState, pwrState):

        ## Aqui tem que mudar no KILO.
        uuid = instance['uuid'        ],
        name = instance['display_name'];
        vcpu = instance['vcpus'       ];
        memo = instance['memory_mb'   ];
        disk = instance['root_gb'     ];

        mcts = mctState;
        pwrs = pwrState;

        ## Prepare the query:
        query  = "INSERT INTO INSTANCES (";
        query += "uuid, name, vcpu, disk, memory, mct_state, pwr_state";
        query += ") VALUES (%s, %s, %s, %s, %s, %s, %s)";
        value  = (uuid[0], name, vcpu, memo, disk, mcts, pwrs);

        valRet = self.__dbConnection.insert_query(query, value);
       
        self.instanceDict[uuid[0]] = {
            'name' : name,
            'vcpu' : vcpu,
            'memo' : memo,
            'disk' : disk,
            'mcts' : mcts,
            'pwrs' : pwrs
        }

        return 0;


    ##
    ## BRIEF: remove a intances line from table.
    ## ------------------------------------------------------------------------
    ## @PARAM uuid == instance unique identifier.
    ##
    def remove(self, uuid):
        query = "DELETE FROM INSTANCES WHERE uuid='" + uuid + "'";

        valRet = self.__dbConnection.delete_query(query);

        ## Remove from dictionary:
        del self.instanceDict[uuid];

        return 0;


    ##
    ## BRIEF: get vm mct status
    ## ------------------------------------------------------------------------
    ## @PARAM uuid == vm uuid.
    ##
    def get_mct_state(self, uuid):

        ## Select query:
        dbQuery = "SELECT mct_state FROM INSTANCES WHERE uuid='"+str(uuid)+"'";

        dataReceived = [] or self.__dbConnection.select_query(dbQuery);

        if dataReceived != []:
            return dataReceived[0][0];

        return 'NOT_FOUND';


    ##
    ## BRIEF: get vm pwr state.
    ## ------------------------------------------------------------------------
    ## @PARAM uuid == vm uuid.
    ##
    def get_pwr_state(self, uuid):

        ## Select query:
        dbQuery = "SELECT pwr_state FROM INSTANCES WHERE uuid='"+str(uuid)+"'";

        dataReceived = [] or self.__dbConnection.select_query(dbQuery);

        if dataReceived != []:
            return dataReceived[0][0];

        return 'NOT_FOUND';


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM uuid  ==
    ## @PARAM state ==
    ##
    def change_pwr_state(self, uuid, state):
        query  = "UPDATE INSTANCES SET pwr_state='" + str(state) + "' ";
        query += "WHERE uuid='" + str(uuid) + "'";

        valRet = self.__dbConnection.update_query(query);

        self.instanceDict[uuid]['pwrs'] = state;

        return 0;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM uuid  ==
    ## @PARAM state ==
    ##
    def change_mct_state(self, uuid, state):
        query  = "UPDATE INSTANCES SET mct_state='" + str(state) + "' ";
        query += "WHERE uuid='" + str(uuid) + "'";

        valRet = self.__dbConnection.update_query(query);

        self.instanceDict[uuid]['mcts'] = state;

        return 0;



    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM uuid  ==
    ##
    def get_instance(self, uuid):
        instance = self.instanceDict[uuid];
        instance['uuid'] = uuid;

        ## TODO: mudar!!!!!!! tem que buscar atualizado.
        return instance;
## END.








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
   instance = MCT_Instance();

## EOF.
