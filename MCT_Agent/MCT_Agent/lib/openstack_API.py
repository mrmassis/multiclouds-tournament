#!/usr/bin/python




import os;
import time;

from keystoneclient.auth.identity import v2,v3
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
VERSION = 2;




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

        ## If you have PROJECT_NAME instead of a PROJECT_ID, use the string la
        ## bel project_name parameter. Similarly, if your cloud uses keystonv3
        ## and you have a DOMAIN_NAME or DOMAIN_ID, provide it as user_domain_
        ## (name|id) and if you are using a PROJECT_NAME also provide the doma
        ## in information as project_domain_(name|id).
        auth = v3.Password(auth_url            = cfg['auth'],
                           username            = cfg['user'],
                           password            = cfg['pswd'],
                           project_name        = cfg['proj'],
                           user_domain_name    = cfg['user_domain_name'],
                           project_domain_name = cfg['proj_domain_name']);

        ## Ponto de contato para os servicos do OpenStack. Armazena as creden-
        ## ciais e informacoes requeridas para comunicacao.  
        keystoneSession = session.Session(auth=auth);

        self.__nova = client.Client(VERSION, session = keystoneSession);


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
        img = self.__nova.images.find  (name = imgL);
        flv = self.__nova.flavors.find (name = flvL);
        net = self.__nova.networks.find(label= netL);

        ## Create a new server (instance) into the openstack (avoid ...):
        server=self.__nova.servers.create(name             =vmsL,  
                                          image            =img.id, 
                                          flavor           =flv.id, 
                                          nics             =[{'net-id':net.id}],
                                          availability_zone=zoneName);

        status = server.status;

        while status == 'BUILD':
            time.sleep(5);

            ## Retrieve the server object again so the status field updates:
            server = self.__nova.servers.get(server.id)
            status = server.status;
 
        try:
            destId = server.id;
        except:
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
       except novaclient.exceptions.NotFound as error:
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

                time.sleep(5);

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
       except novaclient.exceptions.NotFound as error:
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

                time.sleep(5);

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
       except novaclient.exceptions.NotFound as error:
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

                time.sleep(5);

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
## END.       








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    config = {    
        'auth' : 'http://30.0.0.7:5000/v3',
        'user' : 'mct',
        'pswd' : 'password',
        'proj' : 'mct',
        'user_domain_name':'default',
        'proj_domain_name':'default'
    };

    framework = MCT_Openstack_Nova(config);

    vmsL = 'teste';
    imgL = 'cirros-0.3.4-x86_64';
    flvL = 'm1.tiny';
    netL = 'demo-net';

    ##
    valret = framework.create_instance(vmsL, imgL, flvL, netL);

    print 'CREATE ---------------------------------------------------------- ';
    print valret[0]
    print valret[1]

    valret =  framework.delete_instance(valret[1]);

    print 'DELETE ---------------------------------------------------------- ';
    print valret[0]
    print valret[1]
## EOF.

