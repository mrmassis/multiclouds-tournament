#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
__all__ = ['MCT_Openstack_Nova'];

import os;
import time;
import sys;

from keystoneclient.auth.identity import v2,v3;
from keystoneclient               import session;
from novaclient                   import client;








###############################################################################
## DESCRIPTION                                                              ##
###############################################################################
## Intance objct fields:
# 'HUMAN_ID'
# 'NAME_ATTR'
# 'OS-DCF:diskConfig'
# 'OS-EXT-AZ:availability_zone'
# 'OS-EXT-SRV-ATTR:host'
# 'OS-EXT-SRV-ATTR:hypervisor_hostname'
# 'OS-EXT-SRV-ATTR:instance_name'
# 'OS-EXT-STS:power_state'
# 'OS-EXT-STS:task_state'
# 'OS-EXT-STS:vm_state'
# '__class__'
# '__delattr__'
# '__dict__'
# '__doc__'
# '__eq__'
# '__format__'
# '__getattr__'
# '__getattribute__'
# '__hash__'
# '__init__'
# '__module__'
# '__new__'
# '__reduce__'
# '__reduce_ex__'
# '__repr__'
# '__setattr__'
# '__sizeof__'
# '__str__'
# '__subclasshook__'
# '__weakref__'
# '_add_details'
# '_info'
# '_loaded'
# 'accessIPv4'
# 'accessIPv6'
# 'add_fixed_ip'
# 'add_floating_ip'
# 'add_security_group'
# 'addresses'
# 'backup'
# 'change_password'
# 'clear_password'
# 'config_drive'
# 'confirm_resize'
# 'create_image'
# 'created'
# 'delete'
# 'diagnostics'
# 'evacuate'
# 'flavor'
# 'get'
# 'get_console_output'
# 'get_password'
# 'get_spice_console'
# 'get_vnc_console'
# 'hostId'
# 'human_id'
# 'id'
# 'image'
# 'interface_attach'
# 'interface_detach'
# 'interface_list'
# 'is_loaded'
# 'key_name'
# 'links'
# 'live_migrate'
# 'lock'
# 'manager'
# 'metadata'
# 'migrate'
# 'name'
# 'networks'
# 'pause'
# 'progress'
# 'reboot'
# 'rebuild'
# 'remove_fixed_ip'
# 'remove_floating_ip'
# 'remove_security_group'
# 'rescue'
# 'reset_network'
# 'reset_state'
# 'resize'
# 'resume'
# 'revert_resize'
# 'security_groups'
# 'set_loaded'
# 'start'
# 'status'
# 'stop'
# 'suspend'
# 'tenant_id'
# 'unlock'
# 'unpause'
# 'unrescue'
# 'update'
# 'updated'
# 'user_id'








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
NOVA_VERSION = 2;
TIME_TO_WAIT = 2;

INSTANCE_UNKNOW_ERROR   = 'NOSTATE'; 
INSTANCE_LIMITS_REACHED = 'NOSTATE';








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Openstack_Nova:

    """
    ---------------------------------------------------------------------------
    PUBLIC METHODS:
    * create_intance   == create a new instance.
    * delete_intance   == delete a existent instance.
    * suspend_instance == suspend an instance.
    * resume_instance  == resume an instance.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ## 
    ###########################################################################
    __nova = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ## 
    ###########################################################################
    def __init__(self, cfg):
        authUrl = cfg['auth'] + cfg['keystone_version'];

        ## Settig project ID:
        self.__project = cfg['proj'];

        ## If you have PROJECT_NAME instead of a PROJECT_ID, use the string la
        ## bel project_name parameter. Similarly, if your cloud uses keystonv3
        ## and you have a DOMAIN_NAME or DOMAIN_ID, provide it as user_domain_
        ## (name|id) and if you are using a PROJECT_NAME also provide the doma
        ## in information as project_domain_(name|id).
        if   cfg['keystone_version'] == 'v3':
            auth = v3.Password(auth_url            = authUrl,
                               username            = cfg['user'],
                               password            = cfg['pswd'],
                               project_name        = self.__project,
                               user_domain_name    = cfg['user_domain_name'],
                               project_domain_name = cfg['proj_domain_name']);

        elif cfg['keystone_version'] == 'v2.0':
            auth = v2.Password(auth_url            = authUrl,
                               username            = cfg['user'],
                               password            = cfg['pswd'],
                               tenant_name         = self.__project);

        ## Ponto de contato para os servicos do OpenStack. Armazena as creden-
        ## ciais e informacoes requeridas para comunicacao.  
        keystoneSession = session.Session(auth=auth);

        self.__nova = client.Client(NOVA_VERSION, session = keystoneSession);


    ###########################################################################
    ## PUBLIC METHODS                                                        ## 
    ###########################################################################
    ##
    ## Brief: create a new instance.
    ## ------------------------------------------------------------------------
    ## @PARAM vmsL = name of instance (virtual machine server - vms).
    ## @PARAM imgL = name of image.
    ## @PARAM flvL = name of selected flavor.
    ## @PARAM netL = name of network.
    ## @PARAM key  = keypair injected in instance.
    ##
    def create_instance(self, vmsL, imgL, flvL, netL, key=''):
        zoneName = 'nova';

        ## The Compute (nova) python bindings enable you to get an artefact obj
        ## by name.
        flv = self.__nova.flavors.find(name = flvL);
        img = self.__nova.images.find (name = imgL);

        try:
            ## Check the max vm instances are grant to the project:
            maxInstQuota=self.__nova.quotas.defaults(self.__project).instances;
            
            ## Max instances in executing.
            totalInstances = len(self.__nova.servers.list());

            ## Check if the instances number disponible has reached to the end.
            if (totalInstances + 1) <= maxInstQuota:

                ## Create a new server instance (virtual machine) into the open
                ## stack:
                server=self.__nova.servers.create(name   = vmsL,
                                                  image  = img.id,
                                                  flavor = flv.id,
                                                  availability_zone=zoneName);
                status = server.status;

                while status == 'BUILD':
                    time.sleep(TIME_TO_WAIT);

                    ## Retrieve the server object again so the status field updates:
                    server = self.__nova.servers.get(server.id)
                    status = server.status;

            ## The virtual machine instances has reached:
            else:
                status = INSTANCE_LIMIT_REACHED;

            destId = server.id;

        except Exception as error:
            status = INSTANCE_UNKNOW_ERROR;
            destId = '';

        return (status, destId);


    ##
    ## Brief: delete a existent instance.
    ## ------------------------------------------------------------------------
    ## @PARAM instanceId = id of instance (virtual machine server - vms).
    ##
    def delete_instance(self, instanceId):

       ## Get the intance's status:
       try:
           server = self.__nova.servers.find(id = instanceId);
           status = server.status;
       except:
           status = 'ERROR';

       ## Case the intance (id) status is "active or not_found". Nothing to do!
       if status == 'ACTIVE':

            ## Procedure to the delete:
            server.delete();
            server.status;

            while status == 'ACTIVE':
                ## Retrieve the server object again so the status field updates:
                try:
                    server = self.__nova.servers.get(server.id)
                    status = server.status;
                except:
                    status = 'HARD_DELETED';

                time.sleep(TIME_TO_WAIT);

       return (status, '');


    ##
    ## Brief: suspend an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM instanceId = id of instance (virtual machine server - vms).
    ##
    def suspend_instance(self, instanceId):

       ## Get the intance's status:
       try:
           server = self.__nova.servers.find(id = instanceId);
           status = server.status;
       except:
           status = 'ERROR';

       ## Case the intance (id) status is "active or not_found". Nothing to do!
       if status == 'ACTIVE':

            ## Procedure to the suspend:
            server.suspend();
            server.status;

            while status == 'ACTIVE':
                ## Retrieve the server object again so the status field updates:
                try:
                    server = self.__nova.servers.get(server.id)
                    status = server.status;
                except:
                    pass;

                time.sleep(TIME_TO_WAIT);

       return status;


    ##
    ## Brief: resume an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM instanceId = id of instance (virtual machine server - vms).
    ##
    def resume_instance(self, instanceId):

       ## Get the intance's status:
       try:
           server = self.__nova.servers.find(id = instanceId);
           status = server.status;
       except exceptions.NotFound as error:
           status = 'ERROR';

       ## Case the intance (id) status is "active or not_found". Nothing to do!
       if status == 'SUSPENDED':

            ## Procedure to the resume:
            server.resume();
            server.status;

            while status == 'SUSPENDED':
                ## Retrieve the server object again so the status field updates:
                try:
                    server = self.__nova.servers.get(server.id)
                    status = server.status;
                except:
                    pass;

                time.sleep(TIME_TO_WAIT);

       return status;


    ##
    ## Brief: get the status from a instance.
    ## ------------------------------------------------------------------------
    ## @PARAM intanceId == string identificadora da instancia de VM.
    ##
    def get_instance_status(self, instanceId):

        instance = self.__nova.servers.find(id=instanceId);

        if instance != '':
            addresses= instance.addresses;
            instStats= instance.status;
            taskStats= getattr(instance, 'OS-EXT-STS:task_state');


    ##
    ## Brief: get the quota to project.
    ## ------------------------------------------------------------------------
    ## 
    def get_quota(self):

        defaultQuotas = {};

        try:
            valRet = self.__nova.quotas.defaults(self.__project).to_dict();

            defaultQuotas['vcpus' ] = valRet['cores'];
            defaultQuotas['memory'] = valRet['ram'  ];
            defaultQuotas['disk'  ] = 0;

        except:
            defaultQuotas['vcpus' ] = 0;
            defaultQuotas['memory'] = 0;
            defaultQuotas['disk'  ] = 0;

        return defaultQuotas;
## END.       








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    config = {
        'keystone_version' : 'v2.0',
        'auth'             : 'http://controller:5000/',
        'user'             : 'mct',
        'pswd'             : 'password',
        'proj'             : 'mct',
        'user_domain_name' :'default',
        'proj_domain_name' :'default'
    };

    framework = MCT_Openstack_Nova(config);
  
    try:
        if sys.argv[1] == 'create':

            vmsL = sys.argv[2];
            imgL = 'cirros-0.3.3-x86_64';
            flvL = 'm1.tiny';
            netL = 'demo-net';

            ## create 
            valret = framework.create_instance(vmsL, imgL, flvL, netL);

            print 'CREATE -------------------------------------------------- ';
            print valret[0];
            print valret[1];

        elif sys.argv[1] == 'delete':

            valret =  framework.delete_instance(sys.argv[2]);

            print 'DELETE --------------------------------------------------- ';
            print valret[0];
            print valret[1];

    except:
        print 'Usage: openstackAPI create <name>'
        print 'Usage: openstackAPI delete <uuid>'
        print ''
## EOF.

