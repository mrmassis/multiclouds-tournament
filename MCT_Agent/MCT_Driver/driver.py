import ConfigParser;
import contextlib;
import socket;
import json;
import hashlib;
import time;
import json;
import pika;


from oslo.config           import cfg
from nova.compute          import power_state
from nova.compute          import task_states
from nova.console          import type as ctype
from nova                  import db
from nova                  import exception
from nova.i18n             import _
from nova.openstack.common import jsonutils
from nova.openstack.common import log as logging
from nova                  import utils
from nova.virt             import diagnostics
from nova.virt             import driver
from nova.virt             import virtapi
from multiprocessing            import Process, Queue
from nova.virt.mct.lib.database import Database





###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE = '/etc/mct/mct_drive.ini';

## This is a dictionary of dictionary.Each position is a dictionary that repre-
## sent a request pendind to MCT_Agent via AMQP.
REQUEST_PENDING_TIMEOUT = 5;
REQUEST_PENDING = {};

ORIG_ADDR = '10.0.0.30';
PLAYER_ID = 'Player1';

TESTE = {'b':'1'}


CONF = cfg.CONF;
CONF.import_opt('host', 'nova.netconf');

LOG = logging.getLogger(__name__)


_FAKE_NODES = None


def set_nodes(nodes):
    """Sets MCT_Driver's node.list.

    It has effect on the following methods:
        get_available_nodes()
        get_available_resource
        get_host_stats()

    To restore the change, call restore_nodes()
    """
    global _FAKE_NODES
    _FAKE_NODES = nodes


def restore_nodes():
    """Resets MCT_Driver's node list modified by set_nodes().

    Usually called from tearDown().
    """
    global _FAKE_NODES
    _FAKE_NODES = [CONF.host]



PENDING = {};

##
## BRIEF: insert a request into the pending data structure.
## ------------------------------------------------------------------------
## @PARAM idx == request index.
##
def insert_request_pending(idx):
        global PENDING;

        ## LOG:
        LOG.info('[FUNCTION INSERT] PENDING INDEX: %s', idx);

        request = {
            'status_request': 'waiting',
            'data'          : {}
        }

        PENDING[idx] = request;
        LOG.info(PENDING)

        return 0;




##
## BRIEF: update a entry in pending dictionary.
## ------------------------------------------------------------------------
## @PARAM idx   == request index.
## @PARAM data == data to update in request entry.
##
def update_request_pending(idx, data):
        global PENDING

        ## LOG:
        LOG.info('[FUNCTION UPDATE] UPDATE ENTRY: %s', idx);

        if idx in PENDING:
            PENDING[idx]['status_request'] = 'ready';
            PENDING[idx]['data']           = data;

        LOG.info(PENDING)
        return 0;




##
## BRIEF: remove a request from the pending data structure.
## ------------------------------------------------------------------------
## @PARAM idx == request index.
##
def remove_request_pending(idx):
        global PENDING;

        ## LOG:
        LOG.info('[FUNCTION REMOVE] UNPENDING INDEX: %s', idx);

        del PENDING[idx];
        return 0;
##



###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Communication(Process):

    """
    Class MCT_Communication:perform the communication to the MCT_Agent service.
    --------------------------------------------------------------------------
    PUBLIC METHODS:
    ** run      == main loop.
    ** callback == method invoked when the pika receive a message.
    ** publish  == publish a message by the AMQP to MCT_Agent.
    ** pooling  == check if the request pending was received.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __pending      = {};
    __chnP         = None;
    __chnC         = None;
    __config       = None;
    __dbConnection = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, dbConnection):
        super(MCT_Communication, self).__init__();

        ## LOG:
        LOG.info('[MCT_COMMUNICATION] INITIALIZE COMMUNICATION OBJECT!');

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        self.__config = self.__get_config(CONFIG_FILE);

        ## Intance a new object to handler all operation in the local database
        #self.__dbConnection = Database(self.__config['database']);
        self.__dbConnection = dbConnection;

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        self.__init_consume(self.__config['amqp_consume']);

        ## Instantiates an object to perform the publication of AMQP messages.
        self.__init_publish(self.__config['amqp_publish']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## Brief: main loop.
    ## ------------------------------------------------------------------------
    ##
    def run(self):

        queue = self.__config['amqp_consume']['queue_name'];

        ## Consume to the broker and binds messages for the consumer_tag to the
        ## consumer callback. 
        self.chnC.basic_consume(self.callback, queue, no_ack=False);

        ## Processes I/O events and dispatches timers and basic_consume callba-
        ## cks until all consumers are cancelled.
        self.chnC.start_consuming();


    ##
    ## BRIEF: method invoked when the pika receive a message.
    ## ------------------------------------------------------------------------
    ## @PARAM pika.Channel              channel    = the communication channel.
    ## @PARAM pika.spec.Basic.Deliver   method     = 
    ## @PARAM pika.spec.BasicProperties properties = 
    ## @PARAM str                       message    = message received.
    ##
    def callback(self, channel, method, properties, message):

        ## Send to source an ack msg to ensuring that the message was received.
        self.chnC.basic_ack(method.delivery_tag);

        ## LOG:
        LOG.info('[MCT_COMMUNICATION] MESSAGE RECEIVED: %s', message);

        ## Convert the json format to a structure than can handle by the python
        message = json.loads(message);

        ## Insert the message received into the database.
        dbQuery = "INSERT INTO REQUEST (request_id, message) VALUES (%s, %s)";
        dbValue = (message['reqId'], str(message['data']));
       
        self.__dbConnection.insert_query(dbQuery, dbValue);



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

        ##
        properties = pika.BasicProperties(**propertiesData);

        ## Serialize object to a JSON formatted str using this conversion table
        ## If ensure_ascii is False, the result may contain non-ASCII characte-
        ## rs and the return value may be a unicode instance.
        jData = json.dumps(message, ensure_ascii=False);

        ## Insert the current request in the structure that represents the req-
        ## uests who are waiting for response.
        #self.__insert_request_pending(message['reqId']);
        #insert_request_pending(message['reqId']);

        ## Publish to the channel with the given exchange,routing key and body.
        ## Returns a boolean value indicating the success of the operation.
        ack = self.chnP.basic_publish(self.__config['amqp_publish']['exchange'], 
                                      self.__config['amqp_publish']['route'], 
                                      jData, 
                                      properties);

        self.a = 'False'
        return ack;


    ##
    ## BRIEF: check if the request pending was received.
    ## ------------------------------------------------------------------------
    ## @PARAM idx == request index.
    ##
    def pooling(self, idx):

        ## LOG:
        LOG.info('[MCT_COMMUNICATION] POOLING!');

        request = {
            'status_request': 'waiting',
            'data'          : {}
        }

        if idx in self.__pending:
            LOG.info('[MCT_COMMUNICATION] %s', self.__pending); 

            if self.__pending[idx] == 'ready':
                ## Copy the status and put in response. This value will be used
                ## by the method that invoking the pooling.
                request['status_request'] = 'ready';

                ## Get from list the all returned data from 'MCT_Agent'. The re
                ## turn is a dictionary. 
                request['data'] = self.__pending[idx]['data'];

                ## Remove the entry from the list of requests that wainting for
                ## return.
                #self.__remove_request_pending(idx);
                remove_request_pending(idx);

        return request;
    

    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: Initialize the inherited class RabbitMQ_Consume with the paramete
    ##        rs defined in the configuration file.
    ## ------------------------------------------------------------------------
    ## @PARAM dict cfg == amqp consume parameters.
    ##
    def __init_consume(self, cfg):

        ## Connection parameters object that is passed into the connection ada-
        ## pter upon construction. 
        parameters = pika.ConnectionParameters(host=cfg['address']);

        ## The BlockingConnection creates a layer on top of Pika's asynchronous
        ## core providing methods that will block until their expected response
        ## has returned. 
        connection = pika.BlockingConnection(parameters);

        ## Create a new channel with the next available channel number or pass
        ## in a channel number to use. 
        self.chnC = connection.channel();

        ## This method creates an exchange if it does not already exist, and if
        ## the exchange exists, verifies that it is of the correct and expected
        ## class.
        self.chnC.exchange_declare(exchange=cfg['exchange'],type='direct');

        ## Declare queue, create if needed. This method creates or checks a qu-
        ## eue.
        result = self.chnC.queue_declare(queue=cfg['queue_name'],durable=True);

        ## Bind the queue to the specified exchange:
        self.chnC.queue_bind(exchange    = cfg['exchange'], 
                             queue       = cfg['queue_name'],
                             routing_key = cfg['route']);

        ## Specify quality of service. This method requests a specific quality
        ## of service. 
        self.chnC.basic_qos(prefetch_count=1);


    ##
    ## BRIEF: instantiates an object to perform the publication of AMQP msgs.
    ## ------------------------------------------------------------------------
    ## @PARAM dict cfg == amqp publish parameters.
    ##
    def __init_publish(self, cfg):

        ## Connection parameters object that is passed into the connection ada-
        ## pter upon construction. 
        parameters = pika.ConnectionParameters(host=cfg['address']);

        ## The BlockingConnection creates a layer on top of Pika's asynchronous
        ## core providing methods that will block until their expected response
        ## has returned. 
        connection = pika.BlockingConnection(parameters);

        ## Create a new channel with the next available channel number or pass
        ## in a channel number to use. 
        self.chnP = connection.channel();

        ## This method creates an exchange if it does not already exist, and if
        ## the exchange exists, verifies that it is of the correct and expected
        ## class.
        self.chnP.exchange_declare(exchange=cfg['exchange'], type='direct');

        ## Confirme delivery.
        self.chnP.confirm_delivery;


    ##
    ## BRIEF: insert a request into the pending data structure.
    ## ------------------------------------------------------------------------
    ## @PARAM idx == request index.
    ##
    def __insert_request_pending(self, idx):

        ## LOG:
        LOG.info('[MCT_COMMUNICATION] PENDING INDEX: %s', idx);

        request = {
            'status_request': 'waiting',
            'data'          : {}
        }

        self.__pending[idx] = request;
        LOG.info(self.__pending)
        
        return 0;


    ##
    ## BRIEF: remove a request from the pending data structure.
    ## ------------------------------------------------------------------------
    ## @PARAM idx == request index.
    ##
    def __remove_request_pending(self, idx):

        ## LOG:
        LOG.info('[MCT_COMMUNICATION] UNPENDING INDEX: %s', idx);

        del self.__pending[idx];
        return 0;


    ##
    ## BRIEF: update a entry in pending dictionary.
    ## ------------------------------------------------------------------------
    ## @PARAM idx   == request index.
    ## @PARAM data == data to update in request entry.
    ##
    def __update_request_pending(self, idx, data):
        LOG.info(self.__pending)
        ## LOG:
        LOG.info('[MCT_COMMUNICATION] UPDATE ENTRY: %s', idx);

        if idx in self.__pending:
            self.__pending[idx]['status_request'] = 'ready';
            self.__pending[idx]['data']           = data;


        return 0;


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








class Instance(object):

    """
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    name = None;
    uuid = None;
    state= None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, name, state, uuid):
        self.name  = name;
        self.state = state;
        self.uuid  = uuid;
 
    def __getitem__(self, key):
        return getattr(self, key);

## EOF.








class MCT_Agent(object):


    """
    Class MCT_Agent: interface layer between MCT_Agent service and MCT_Drive.
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
    __pending       = {};
    __dbConnection  = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):
        
        ## Power state is the state we get by calling virt driver on a particu-
        ## lar domain. The hypervisor is always considered the authority on the
        ## status of a particular VM and the power_state in the DB should be vi
        ## ewed as a snapshot of the VMs's state in the (recent) past.It can be
        ## periodically updated,and should also be updated at the end of a task
        ## if the task is supposed to affect power_state.
        ##
        ## NOSTATE   = 0x00
        ## RUNNING   = 0x01
        ## PAUSED    = 0x03
        ## SHUTDOWN  = 0x04 # the VM is powered off
        ## CRASHED   = 0x06
        ## SUSPENDED = 0x07
        ##
        self.__returnState = {

            '0' : power_state.NOSTATE ,
            '1' : power_state.RUNNING ,
            '2' : power_state.PAUSED  ,
            '3' : power_state.SHUTDOWN,
            '6' : power_state.CRASHED ,
            '7' : power_state.SUSPENDED
        };

        ## Get all configs parameters presents in the config file localized in
        ## CONFIG_FILE path.
        config = self.__get_config(CONFIG_FILE);

        ## Intance a new object to handler all operation in the local database
        self.__dbConnection = Database(config['database']); 

        ## Instance the object that will communicate with MCT_Agent. Running in
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

        ## Send the request to the MCT_Agent via asynchronous protocol (AMPQP).
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
        LOG.info('[MCT_AGENT] GETTING MCT RESOURCE INFORMATION!');

        ## Create an idx to identify the request for the resources information.
        idx = self.__create_index();

        ## Protocol: [000] get player status!
        dataToSend = {
            'code'    : 0,
            'playerId': PLAYER_ID,
            'status'  : 0,
            'reqId'   : idx,
            'retId'   : '',
            'origAdd' : ORIG_ADDR,
            'destAdd' : '',
            'data'    : {}
        };

        ## Send the request to the MCT_Agent via asynchronous protocol (AMPQP).
        self.__send_to_agent(dataToSend);

        ## Waiting for the answer arrive. When the status change status get it.
        while True:

            ## Mount the select query: 
            dbQuery  = "SELECT message FROM REQUEST WHERE ";
            dbQuery += "request_id='" + idx + "'";

            dataReceived = [] or self.__dbConnection.select_query(dbQuery);

            if dataReceived != []:
                ## TODO:
                LOG.info(dataReceived);

            ## Wating for a predefined time to check (pooling) the list again.
            time.sleep(REQUEST_PENDING_TIMEOUT);

        ## LOG:
        LOG.info('[MCT_AGENT] DATA RECEIVED: %s', dataReceived['data']);

        ## Return the all datas about resouces avaliable in player's division.
        return dataReceived['data'];


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
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








class MCT_Driver(driver.ComputeDriver):

    """
    Class: MultiCloud Tournament Driver.
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    capabilities = None;
    instances    = {};
    __mounts     = {};
    __interfaces = {};
    mct          = None;
    vcpus        = None;
    memory_mb    = None;
    local_gb     = None;
    __resourcesStatusBase = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM virtapi   ==
    ## @PARAM read_only ==
    ## 
    def __init__(self, virtapi, read_only=False):
        ## Inicializa a VIRTAPI:
        super(MCT_Driver, self).__init__(virtapi);

        self.capabilities = {
            "has_imagecache"   : True,
            "supports_recreate": True,
        };

        if not _FAKE_NODES:
            set_nodes([CONF.host])

        ## 
        self.mct = MCT_Agent();

        ## TODO: Check all fields:
        self.__resourcesStatusBase = {
            'hypervisor_type'     : 'mct',
            'hypervisor_version'  : 1000000,
            'hypervisor_hostname' : 'mct_agent',
            'cpu_info'            : {},
            'disk_available_least': 0,
            #'supported_instances' : [[null, "fake", null]],
            'numa_topology'       : None,
        };


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ## 
    ## BRIEF: initialize anything that is necessary for the driver to function
    ##        including catching up with currently running VM's on the given
    ##        host.
    ## ------------------------------------------------------------------------
    ## @PARAM host == .
    ##
    def init_host(self, host):
        LOG.info("[MCT_Drive] init_host!");
        return


    ##
    ## BRIEF: return the name of all the instances know to the virtualization
    ##        layer, as a list.
    ## ------------------------------------------------------------------------
    ## @RETURN a List.
    ##
    def list_instances(self):
        LOG.info("[MCT_Drive] list_instances!");
        LOG.info(self.instances.keys());
 
        ## Tem que ir ateh o MCT_Agent e obter todas as VMs executadas remota-
        ## mente com origem nesse host.
        return self.instances.keys();


    ##
    ## BRIEF: return the UUIDS of all the instances know to the virtualization
    ##        layer, as a list.
    ## ------------------------------------------------------------------------
    ## @RETURN a List.
    ##
    def list_instance_uuids(self):
        LOG.info("[MCT_Drive] list_instances_uuids!");

        ## Tem que ir ateh o MCT_Agent e obter todas as VMs executadas remota-
        ## mente com origem nesse host.
        return [self.instances[name].uuid for name in self.instances.keys()]


    ##
    ## BRIEF: plug virtual interfaces (VIF) into the given instance at boot ti-
    ##        me (the counter action is unplug_vif).
    ## ------------------------------------------------------------------------
    ## @PARAM instance     == (nova.objects.instance.Instance) the instance wi-
    ##                        ch gets VIFs plugged.
    ## @PARAM network_info == (nova.network.model.NetworkInfo) the object which
    ##                        contains information about the VIFs to plug.
    ##
    ## @RETURN None.
    ## 
    def plug_vifs(self, instance, network_info):
        LOG.info("[MCT_Drive] plug_vifs!");

        ## Aqui ou no MCT_Agent serah necessario realizar um trabalho de mapea-
        ## mento porque a rede sera em um contexto remoto diferente do local.
        pass


    ##
    ## BRIEF: unplug virtual interfaces (VIF) from networks.
    ## ------------------------------------------------------------------------
    ## @PARAM instance     == (nova.objects.instance.Instance) the instance wi-
    ##                        ch gets VIFs plugged.
    ## @PARAM network_info == (nova.network.model.NetworkInfo) the object which
    ##                        will be plugged.
    ## 
    def unplug_vifs(self, instance, network_info):
        LOG.info("[MCT_Drive] unplug_vifs!");
        pass


    ##
    ## BRIEF: Create a new "instance/VM/domain" on the virtualization platform
    ##        Once this successfully completes, the instance should be running
    ##        (power_state.RUNNING). If this fails, any partial instance shou-
    ##        ld be completely cleaned up, and the virtualization platform sh-
    ##        ould be in the state that it was before this call began. 
    ## ------------------------------------------------------------------------
    ## @PARAM context           == security context;
    ## @PARAM instance          == (nova.objects.instance) Instance This funct-
    ##                             ion should use the data there to guide the
    ##                             creation of the new instance.
    ## @PARAM image_meta        == (nova.objects.ImageMeta) The metadata of the
    ##                             image of the instance.
    ## @PARAM injected_files    == User files to inject into instance.
    ## @PARAM admin_password    == Administrator password to set in instance.
    ## @PARAM network_info      == get_instance_nw_info();
    ## @PARAM block_device_info == Information about block devices to be attac-
    ##                             hed to the instance.
    ##
    def spawn(self, context, instance, image_meta, injected_files,
              admin_password, network_info=None, block_device_info=None):

        ## Create a new dictionary struct with will be contain the parameter to
        ## intance a new VM.
        data = {
            'instance': instance,
            'image'   : image_meta,
            'injected': injected_files,
            'password': admin_password,
            'network' : network_info,
            'storage' : block_device_info
        }

        ## Research the more apropriated (by the score) player to accept the VM
        ## creation.
        valRet = self.mct.create_instance(data);

        ##
        uuid = instance['uuid'];
        name = instance['name'];

        ##
        mctInstance = Instance(name, valRet, uuid);

        ## 
        self.instances[name] = mctInstance;

        ## LOG:
        LOG.info("[MCT_Drive] Instance Spaw! State: " + str(valRet));


    ##
    ## BRIEF: Destroy the specified instance from the Hypervisor. If the instan
    ##        ce is not found (for example if networking failed), this function
    ##        should still succeed. It's probably a good idea to log a warning 
    ##        in that case. 
    ## ------------------------------------------------------------------------
    ## @PARAM context           == security context;
    ## @PARAM instance          == (nova.objects.instance) Instance This funct-
    ##                             ion should use the data there to guide the
    ##                             creation of the new instance.
    ## @PARAM network_info      == get_instance_nw_info();
    ## @PARAM block_device_info == Information about block devices to be attac-
    ##                             hed to the instance.
    ##
    def destroy(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None):
 
        ## Create a new dictionary struct with will be contain the parameter to
        ## intance a new VM.
        data = {
            'instance': instance,
            'network' : network_info,
            'storage' : block_device_info
        }

        ## Get the instance name to be destroied. The instance object is recei-
        ## ved from parameter list.
        name = instance['name'];

        ## Check if the instance exist.
        if name in self.instances:
            valRet = self.mct.delete_instance(data);

            del self.instances[name];

        else:
            LOG.warning(_("[MCT_Drive] %(name)s not in instances %(inst)s") %
                         {'name': name,
                         'inst' : self.instances}, instance=instance);

        LOG.info("[MCT_Drive] Instance Destroyed!");


    ##
    ## BRIEF: Cleanup the instance resources. Instance should have been destro-
    ##        yed from the Hypervisor before calling this method.
    ## ------------------------------------------------------------------------
    ## @PARAM context           == security context;
    ## @PARAM instance          == (nova.objects.instance) Instance This funct-
    ##                             ion should use the data there to guide the
    ##                             creation of the new instance.
    ## @PARAM network_info      == get_instance_nw_info();
    ## @PARAM block_device_info == Information about block devices to be attac-
    ##                             hed to the instance.
    ## @PARAM destroy_disks     == Indicates if disks should be destroyed.
    ## @PARAM migrate_data      == Implementation specific params.
    ## @PARAM destroy_vifs      == 
    ##
    def cleanup(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None, destroy_vifs=True):


        LOG.info("[MCT_Drive] clenup!");
        pass;


    ##
    ## BRIEF: snapshot the specific instance.
    ## ------------------------------------------------------------------------
    ## @PARAM context           == security context.
    ## @PARAM instance          == nova.object.instance.Instance.
    ## @PARAM name              == 
    ## @PARAM update_task_state == reference to pre-created img that will hold
    ##                             the snapshot.
    ##
    def snapshot(self, context, instance, name, update_task_state):
        LOG.info("[MCT_Drive] snapshot!");

        if instance['name'] not in self.instances:
            raise exception.InstanceNotRunning(instance_id=instance['uuid']);

        update_task_state(task_state=task_states.IMAGE_UPLOADING);


    ##
    ## BRIEF: reboot the specified instance.
    ## ------------------------------------------------------------------------
    ## @PARAM context              == security context.
    ## @PARAM instance             == nova.object.instance.Instance.
    ## @PARAM network_info         == get_instance_nw_info();
    ## @PARAM reboot_type          == either a HARD or SOFT reboot.
    ## @PARAM block_device_info    == Information about block devices to be at-
    ##                                tached to the instance.
    ## @PARAM bad_volumes_callback == function to handle any bad volumes encoun
    ##                                tered.
    ##
    def reboot(self, context, instance, network_info, reboot_type,
               block_device_info=None, bad_volumes_callback=None):
        LOG.info("[MCT_Drive] reboot!");

        ## After this called successfully, the instance's state goes back to po
        ## wer_state.RUNNING. The virtualization plataform should ensure that t
        ## he reboot action has completed successfully even in cases in which t
        ## he undelying domain/vm is paused or halted/stoped.
        pass;


    ##
    ## BRIEF: retrieves the IP addres od the dom0.
    ## ------------------------------------------------------------------------
    ##
    @staticmethod
    def get_host_ip_addr():
        LOG.info("[MCT_Drive] get_host_ip_addr!");
        return '192.168.0.1';



    def set_admin_password(self, instance, new_pass):
        pass

    def inject_file(self, instance, b64_path, b64_contents):
        pass

    def resume_state_on_host_boot(self, context, instance, network_info,
                                  block_device_info=None):
        pass

    def rescue(self, context, instance, network_info, image_meta,
               rescue_password):
        pass

    def unrescue(self, instance, network_info):
        pass

    def poll_rebooting_instances(self, timeout, instances):
        pass

    def migrate_disk_and_power_off(self, context, instance, dest,
                                   flavor, network_info,
                                   block_device_info=None,
                                   timeout=0, retry_interval=0):
        pass

    def finish_revert_migration(self, context, instance, network_info,
                                block_device_info=None, power_on=True):
        pass

    def post_live_migration_at_destination(self, context, instance,
                                           network_info,
                                           block_migration=False,
                                           block_device_info=None):
        pass

    def power_off(self, instance, shutdown_timeout=0, shutdown_attempts=0):
        pass

    def power_on(self, context, instance, network_info, block_device_info):
        pass

    def soft_delete(self, instance):
        pass

    def restore(self, instance):
        pass

    def pause(self, instance):
        pass

    def unpause(self, instance):
        pass

    def suspend(self, instance):
        pass

    def resume(self, context, instance, network_info, block_device_info=None):
        pass



    def attach_volume(self, context, connection_info, instance, mountpoint,
                      disk_bus=None, device_type=None, encryption=None):
        """Attach the disk to the instance at mountpoint using info."""
        instance_name = instance['name']
        if instance_name not in self.__mounts:
            self.__mounts[instance_name] = {}
        self.__mounts[instance_name][mountpoint] = connection_info

    def detach_volume(self, connection_info, instance, mountpoint,
                      encryption=None):
        """Detach the disk attached to the instance."""
        try:
            del self.__mounts[instance['name']][mountpoint]
        except KeyError:
            pass

    def swap_volume(self, old_connection_info, new_connection_info,
                    instance, mountpoint, resize_to):
        """Replace the disk attached to the instance."""
        instance_name = instance['name']
        if instance_name not in self.__mounts:
            self.__mounts[instance_name] = {}
        self.__mounts[instance_name][mountpoint] = new_connection_info

    def attach_interface(self, instance, image_meta, vif):
        if vif['id'] in self.__interfaces:
            raise exception.InterfaceAttachFailed(
                    instance_uuid=instance['uuid'])
        self.__interfaces[vif['id']] = vif

    def detach_interface(self, instance, vif):
        try:
            del self.__interfaces[vif['id']]
        except KeyError:
            raise exception.InterfaceDetachFailed(
                    instance_uuid=instance['uuid'])


    def get_info(self, instance):
        if instance['name'] not in self.instances:
            raise exception.InstanceNotFound(instance_id=instance['name'])
        i = self.instances[instance['name']]

        LOG.info('---->');
        LOG.info(i.state);

        return {'state': i.state,
                'max_mem': 0,
                'mem': 0,
                'num_cpu': 2,
                'cpu_time': 0}





    def get_diagnostics(self, instance_name):
        return {'cpu0_time': 17300000000,
                'memory': 524288,
                'vda_errors': -1,
                'vda_read': 262144,
                'vda_read_req': 112,
                'vda_write': 5778432,
                'vda_write_req': 488,
                'vnet1_rx': 2070139,
                'vnet1_rx_drop': 0,
                'vnet1_rx_errors': 0,
                'vnet1_rx_packets': 26701,
                'vnet1_tx': 140208,
                'vnet1_tx_drop': 0,
                'vnet1_tx_errors': 0,
                'vnet1_tx_packets': 662,
        }

    def get_instance_diagnostics(self, instance_name):
        diags = diagnostics.Diagnostics(state='running', driver='fake',
                hypervisor_os='fake-os', uptime=46664, config_drive=True)
        diags.add_cpu(time=17300000000)
        diags.add_nic(mac_address='01:23:45:67:89:ab',
                      rx_packets=26701,
                      rx_octets=2070139,
                      tx_octets=140208,
                      tx_packets = 662)
        diags.add_disk(id='fake-disk-id',
                       read_bytes=262144,
                       read_requests=112,
                       write_bytes=5778432,
                       write_requests=488)
        diags.memory_details.maximum = 524288
        return diags

    def get_all_bw_counters(self, instances):
        """Return bandwidth usage counters for each interface on each
           running VM.
        """
        bw = []
        return bw

    def get_all_volume_usage(self, context, compute_host_bdms):
        """Return usage info for volumes attached to vms on
           a given host.
        """
        volusage = []
        return volusage

    def get_host_cpu_stats(self):
        stats = {'kernel': 5664160000000L,
                'idle': 1592705190000000L,
                'user': 26728850000000L,
                'iowait': 6121490000000L}
        stats['frequency'] = 800
        return stats

    def block_stats(self, instance_name, disk_id):
        return [0L, 0L, 0L, 0L, None]

    def interface_stats(self, instance_name, iface_id):
        return [0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L]

    def get_console_output(self, context, instance):
        return 'FAKE CONSOLE OUTPUT\nANOTHER\nLAST LINE'

    def get_vnc_console(self, context, instance):
        return ctype.ConsoleVNC(internal_access_path='FAKE',
                                host='fakevncconsole.com',
                                port=6969)

    def get_spice_console(self, context, instance):
        return ctype.ConsoleSpice(internal_access_path='FAKE',
                                  host='fakespiceconsole.com',
                                  port=6969,
                                  tlsPort=6970)

    def get_rdp_console(self, context, instance):
        return ctype.ConsoleRDP(internal_access_path='FAKE',
                                host='fakerdpconsole.com',
                                port=6969)

    def get_serial_console(self, context, instance):
        return ctype.ConsoleSerial(internal_access_path='FAKE',
                                   host='fakerdpconsole.com',
                                   port=6969)

    def get_console_pool_info(self, console_type):
        return {'address': '127.0.0.1',
                'username': 'fakeuser',
                'password': 'fakepassword'}

    def refresh_security_group_rules(self, security_group_id):
        return True

    def refresh_security_group_members(self, security_group_id):
        return True

    def refresh_instance_security_rules(self, instance):
        return True

    def refresh_provider_fw_rules(self):
        pass


    ##
    ## BRIEF: Retrive resource informations. This method is called when "nova-
    ##        compute launches,and as part of a periodic task that records the
    ##        the resuts in the DB.
    ## ------------------------------------------------------------------------
    ## @PARAM nodename == node wich the caller want get resources from a driver
    ##                    that manages only one node can safely ignore this.
    ##
    ## @RETURN (dict) dictionary describing resources.
    ##
    def get_available_resource(self, nodename):

        ## LOG:
        LOG.info("[MCT_Drive] GET AVALIBLE RESOURCES!");

        ## Request to MCT Agent informations about MCT resources. The return is
        ## a dictionary of information resources. These values depend on the di
        ## vision of the player belongs.
        valRet = self.mct.get_resource_inf();

        ## Convert the units to compreensive format. The original forma is "MB".
        if valRet != {}:
            valRet['local_gb_used'] = valRet['local_gb_used'] / 1024;
            valRet['local_gb']      = valRet['local_gb'     ] / 1024;

        ## Copy the status base (fixed values) and concatenate with actual reso
        ## urce informations obtained from MCT.
        actualResourcesStatus = self.__resourcesStatusBase.copy();
        actualResourcesStatus.update(valRet);

        return actualResourcesStatus;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def ensure_filtering_rules_for_instance(self, instance_ref, network_info):
        return

    def get_instance_disk_info(self, instance_name, block_device_info=None):
        return

    def live_migration(self, context, instance_ref, dest,
                       post_method, recover_method, block_migration=False,
                       migrate_data=None):
        post_method(context, instance_ref, dest, block_migration,
                            migrate_data)
        return

    def check_can_live_migrate_destination_cleanup(self, ctxt,
                                                   dest_check_data):
        return

    def check_can_live_migrate_destination(self, ctxt, instance_ref,
                                           src_compute_info, dst_compute_info,
                                           block_migration=False,
                                           disk_over_commit=False):
        return {}

    def check_can_live_migrate_source(self, ctxt, instance_ref,
                                      dest_check_data, block_device_info=None):
        return

    def finish_migration(self, context, migration, instance, disk_info,
                         network_info, image_meta, resize_instance,
                         block_device_info=None, power_on=True):
        return

    def confirm_migration(self, migration, instance, network_info):
        return

    def pre_live_migration(self, context, instance_ref, block_device_info,
                           network_info, disk, migrate_data=None):
        return

    def unfilter_instance(self, instance_ref, network_info):
        return

    def test_remove_vm(self, instance_name):
        """Removes the named VM, as if it crashed. For testing."""
        self.instances.pop(instance_name)


    ##
    ## BRIEF: reboot, shutsdown or powers up the host.
    ## ------------------------------------------------------------------------
    ## @PARAM host   == the target.
    ## @PARAM action == the action.
    ##
    def host_power_action(self, host, action):
        LOG.info("[MCT_Drive] host_power_action!");
        return action;


    ##
    ## BRIEF: start/stop host maintenance window. On start, it triggers the mi-
    ##        gration of all instance to other hosts. Consider the combinantion
    ##        with set_host_enable().
    ## ------------------------------------------------------------------------
    ## @PARAM host == the name of the host whose maintenance mode should be mo-
    ##                fied.
    ## @PARAM mode == if True, go into the maintenance mode. If False, leaving
    ##                the maintenance mode.
    ##
    ## @RETURN (str) on_maintenance if switched to maintenance mode or of_main-
    ##               tenance if maintenance mode got left.
    ##
    def host_maintenance_mode(self, host, mode):
        LOG.info("[MCT_Drive] host_maintenance_mode!");

        if not mode:
            return 'off_maintenance';

        return 'on_maintenance';


    ##
    ## BRIEF: set the abilitity of this host to accept new instances.
    ## ------------------------------------------------------------------------
    ## @PARAM host    ==
    ## @PARAM enabled == if True, the host will accept new instances. If it is
    ##                   False, the host won't accept new instnaces
    ##
    ## @RETURN (str) if the host can accept further instances, return "enabled"
    ##               if further instance shouldn't be scheduled to this host,
    ##               return disabled.
    ##
    def set_host_enabled(self, host, enabled):
        LOG.info("[MCT_Drive] set_host_enable!");

        if enabled:
            return 'enabled';

        return 'disabled';


    ##
    ## BRIEF: get the connector information for the instance for attaching to
    ##        volumes. 
    ## ------------------------------------------------------------------------
    ## @PARAM instance ==  
    ##
    def get_volume_connector(self, instance):
        LOG.info("[MCT_Drive] get_volume_connector!");
 
        ## Connector information is a dictionary representing the ip of the ma-
        ## chine that will be making the connection, the name of the iscsi ini-
        ## tiator and the hostname of the machine as follow:
        connectorInf = {
            'ip'       : '127.0.0.1',
            'initiator': 'fake',
            'host'     : 'fakehost'
        }

        return connectorInf;


    ##
    ## BRIEF: return the nodes name of all nodes managed by the compute service.
    ##        This method is for multi compute-nodes suporte. If a driver suppo
    ##        rt multi compute-nodes, this method returns a list of nodename ma
    ##        naged by the service. Otherwise, this method should return [hyper
    ##        visor_hostname].
    ## ------------------------------------------------------------------------
    ## @PARAM refresh ==  
    ##
    def get_available_nodes(self, refresh=False):
        LOG.info("[MCT_Drive] get_avaliable_nodes!");
        return _FAKE_NODES;


    ##
    ## BRIEF: check access of instance files on the host.
    ## ------------------------------------------------------------------------
    ## @PARAM instance == nova.object.instance.Instance to lookup.
    ##
    ## @RETURN (bool) True if files of an instance with the supplied ID accessi
    ##                ble on the host. False otherwise.
    ##
    def instance_on_disk(self, instance):
        LOG.info("[MCT_Drive] instance_on_disk!");

        ## NOTE: used in rebuild for HA implementation and required for valida-
        ##       tion of access to instance shared disk files.
        return False;
## END.










class FakeVirtAPI(virtapi.VirtAPI):
    def provider_fw_rule_get_all(self, context):
        return db.provider_fw_rule_get_all(context)

    @contextlib.contextmanager
    def wait_for_instance_event(self, instance, event_names, deadline=300,
                                error_callback=None):
        # NOTE(danms): Don't actually wait for any events, just
        # fall through
        yield







class SmallMCT_Driver(MCT_Driver):
    # The api samples expect specific cpu memory and disk sizes. In order to
    # allow the FakeVirt driver to be used outside of the unit tests, provide
    # a separate class that has the values expected by the api samples. So
    # instead of requiring new samples every time those
    # values are adjusted allow them to be overwritten here.

    vcpus = 1
    memory_mb = 8192
    local_gb = 1028
