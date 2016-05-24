#!/usr/bin/python

import keystoneauth1;
import novaclient;
import os;





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
    * create_intance    ==
    * delete_intance    ==
    * reset_instance    ==
    * poweron_instance  ==
    * poweroff_instance ==
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ## 
    ###########################################################################
    __nova = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ## 
    ###########################################################################
    def __init__(self, user, pass, auth, proj):
        ## Obtem a classe de plugin indicado pelo paramentro name == password.
        loader = keystoneauth1.loading.get_plugin_loader('password');

        ## If you have PROJECT_NAME instead of a PROJECT_ID, use the string la
        ## bel project_name parameter. Similarly, if your cloud uses keystonv3
        ## and you have a DOMAIN_NAME or DOMAIN_ID, provide it as user_domain_
        ## (name|id) and if you are using a PROJECT_NAME also provide the doma
        ## in information as project_domain_(name|id).
        ## TODO: automatizar a selecao e escolha.
        auth = loader.Password(auth_url   = auth,
                               username   = user,
                               password   = pass,
                               project_id = proj);

        ## Ponto de contato para os servicos do OpenStack. Armazena as creden-
        ## ciais e informacoes requeridas para comunicacao.  
        session = keystoneauth1.session.Session(auth=auth);

        self.__nova = novalient.client.Client(VERSION, session=session);
     

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
        zoneName = '';

        ## The Compute (nova) python bindings enable you to get an artefact obj
        ## by name.
        img = nova.images.find  (name = imgL);
        flv = nova.flavors.find (name = flvL);
        net = nova.networks.find(label= netL);

        ## Create a new server (instance) into the openstack (avoid ...):
        server = nova.servers.create(name              = vmsL,  
                                     image             = img.id, 
                                     flavor            = flv.id, 
                                     nics              = [{'net-id':net.id}],
                                     availability_zone = zoneName);

        status = server.status;

        while status == 'BUILD':
            time.sleep(5);

            ## Retrieve the server object again so the status field updates:
            server = nova.servers.get(server.id)
            status = server.status;
 
        return status;


    ##
    ## Brief: delete a existent instance.
    ## ------------------------------------------------------------------------
    ## @PARAM vmsL = name of instance (virtual machine server - vms).
    ##
    def delete_instance(self, vmsL):
        try:
            server = nova.servers.find(name=vmsL);
            server.delete();
        except:
            return 0;

        return 1;


    ##
    ## Brief: reset a existent instance.
    ## ------------------------------------------------------------------------
    ## @PARAM vmsL = name of instance (virtual machine server - vms).
    ##
    def reset_instance(self):
        try:
            server = nova.servers.find(name=vmsL);
            server.reboot();
        except:
            return 0;

        return 1;


    ##
    ## Brief: put an instance in power on mode.
    ## ------------------------------------------------------------------------
    ## @PARAM vmsL = name of instance (virtual machine server - vms).
    ##
    def poweron_instance(self):
        try:
            server = nova.servers.find(name=vmsL);
            server.resume();
        except:
            return 0;

        return 1;


    ##
    ## Brief: put an instance in power off mode.
    ## ------------------------------------------------------------------------
    ## @PARAM vmsL = name of instance (virtual machine server - vms).
    ##
    def poweroff_instance(self):
        try:
            server = nova.servers.find(name=vmsL);
            server.suspend();
        except:
            return 0;

        return 1;


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

    user = os.environ['OS_USERNAME'   ];
    pass = os.environ['OS_PASSWORD'   ];
    auth = os.environ['OS_AUTH_URL'   ];
    proj = os.environ['OS_TENANT_NAME'];
    
    framework = MCT_Openstack_Nova(user, pass, auth, proj):

    vmsL = '';
    imgL = '';
    flvL = 'm1.tiny';
    netL = '';

    framework.create_instance(vmsL, imgL, flvL, netL);
## EOF.

