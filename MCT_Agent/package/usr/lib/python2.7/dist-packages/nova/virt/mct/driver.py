import contextlib
import socket


## to JUNO version:
try:
    from nova.openstack.common import log as logging;
    from nova.openstack.common import jsonutils;
    from oslo.config           import cfg;
    from nova.i18n             import _;
    from nova.virt             import virtapi;

## to KILO version:
except:
    from nova.compute          import vm_mode;
    from nova.compute          import arch;
    from nova.compute          import hv_type;
    from oslo_log              import log as logging;
    from oslo_serialization    import jsonutils;
    from oslo_config           import cfg;
    from nova.i18n             import _LW;
    from nova.virt             import hardware;


from nova.compute              import power_state;
from nova.compute              import task_states;
from nova.console              import type as ctype;
from nova                      import db;
from nova                      import exception;
from nova                      import utils;
from nova.virt                 import diagnostics;
from nova.virt                 import driver;

from nova.virt.mct.action    import MCT_Action;
from nova.virt.mct.instances import MCT_Instances;







###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
LOG = logging.getLogger(__name__);
MCT_UNREACHABLE = -5;




###############################################################################
## CLASSES                                                                   ##
###############################################################################
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
    mct          = None;
    vcpus        = None;
    memory_mb    = None;
    local_gb     = None;
    __mounts     = {};
    __interfaces = {};
    __resourcesStatusBase = None;
    __hostname            = None;


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
        super(MCT_Driver, self).__init__(virtapi);

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
        self.returnState = {
            0 : power_state.NOSTATE ,
            1 : power_state.RUNNING ,
            2 : power_state.PAUSED  ,
            3 : power_state.SHUTDOWN,
            6 : power_state.CRASHED ,
            7 : power_state.SUSPENDED
        };

        ## TODO: ver diferenca entre power and task status.

        ## Instance the classe that will be the interface layer between the MCT
        ## drive and MCT_Agent. 
        self.mct = MCT_Action(self.returnState);

        ## Get the machine hostname. It will be the nodename:
        self.__hostname = socket.gethostname();

        ## Fixed resource informations about the "multicloud tournament -- MCT.
        self.__resourcesStatusBase = {
            'hypervisor_type'    : 'mct',
            'hypervisor_version' : utils.convert_version_to_int("0.1"),
            'hypervisor_hostname': self.__hostname,
            'numa_topology'      : None,
            'cpu_info'           : '?'

            #'supported_instances'    : jsonutils.dumps(host_stats['supported_instances']),
            #'pci_passthrough_devices': jsonutils.dumps(host_stats['pci_passthrough_devices']),
        };

        ## Expose the drive (host) capabilities:
        self.capabilities = {
            "has_imagecache"               : False,
            "supports_recreate"            : False,
            "supports_migrate_to_same_host": False,
        };

        ## Create the object that will store the "MCT instances" in execution,
        self.__instances = MCT_Instances();


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ## 
    ## BRIEF: initialize anything that is necessary for the driver to function
    ##        including catching up with currently running VM's on the given
    ##        host.
    ## ------------------------------------------------------------------------
    ## @PARAM host == this host.
    ##
    def init_host(self, host):

        ## Get all "MCT instances" that are running and store in the database.
        self.__instances.recovery_instances();

        LOG.info("INIT HOST: %s", str(host));
        return


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

        ## LOG:
        LOG.info("GET AVALIABLE NODES!");

        return [self.__hostname];



    ## ------------------------------------------------------------------------
    ## INSTANCES
    ## ------------------------------------------------------------------------ 
    ##
    ## BRIEF: get instance information.
    ## ------------------------------------------------------------------------
    ## @PARAM instance == (nova.objects.instance) Instance This function should
    ##                    use the data there to guide the creation of the new
    ##                    instance.
    ##
    def get_info(self, instance):
        ## LOG:
        LOG.info("GET INSTANCE %s INFORMATION!", instance['uuid']);

        uuid = instance['uuid'];

        ## Check if the instance exist. The openstack will be compare the dbase
        ## with local intances dbase.
        if self.__instances.check_exist(uuid) == False:
            raise exception.InstanceNotFound(instance_id=uuid);

        ## Get update instance:
        instance = self.__instances.get_instance(uuid);
        LOG.info(instance);

        ## Send get instance info request to the MCT:
<<<<<<< HEAD
        valRet = self.mct.get_instance_information(instance['uuid']); 
=======
        #valRet = self.mct.get_instance_information(uuid); 
        valRet = {};
>>>>>>> f509b9fea73c54d497522b85885032cfc62642af

        if valRet != {}:
            instanceInfoObj = {};
        else:
            ## instanceinfo object:
            ## state       == the running sate, one of the power_state codes.
            ## max_mem_kb  == (int) the maximum memory in KBytes allowed.
            ## mem_kb      == (int) the memory in KBytes for the instance.
            ## nun_cpu     == (int) the number of virtual CPUs for the instance.
            ## cpu_time_ns == (int) the CPU time used in nano seconds.
            ##
            instanceInfoObj = {
                'state'   : self.returnState[instance['pwrs']],
                'mem'     : instance['memo'],
                'num_cpu' : instance['vcpu'], ## defined by the flavor, can the flavor is diferente in destiny
                'max_mem' : 0,
                'cpu_time': 0
            };

        return instanceInfoObj;


    ##
    ## BRIEF: get diagnostic about the given instance.
    ## ------------------------------------------------------------------------
    ## @PARAM intance_name ==
    ##
    def get_instance_diagnostics(self, instance_name):

        diags = diagnostics.Diagnostics(state='running', driver='fake', hypervisor_os='fake-os', uptime=46664, config_drive=True);

        diags.add_cpu(time=17300000000);

        diags.add_nic(mac_address='01:23:45:67:89:ab',
                      rx_packets=26701,
                      rx_octets=2070139,
                      tx_octets=140208,
                      tx_packets = 662);

        diags.add_disk(id='fake-disk-id',
                       read_bytes=262144,
                       read_requests=112,
                       write_bytes=5778432,
                       write_requests=488)

        diags.memory_details.maximum = 524288;

        return diags;


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------ 
    ## @PARAM instance_name ==
    ##
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


    ##
    ## BRIEF: return the name of all the instances know to the virtualization
    ##        layer, as a list.
    ## ------------------------------------------------------------------------
    ## @RETURN a List.
    ##
    def list_instances(self):

        ## Get all instances names:
        instancesList = self.__instances.get_instances_name();

        ## LOG:
        LOG.info("LIST INSTANCES NAMES: %s", instancesList);

        return instancesList;


    ##
    ## BRIEF: return the UUIDS of all the instances know to the virtualization
    ##        layer, as a list.
    ## ------------------------------------------------------------------------
    ## @RETURN a List.
    ##
    def list_instance_uuids(self):

        ## Get all instances names:
        instancesList = self.__instances.get_instances_uuid();

        ## LOG:
        LOG.info("LIST INSTANCES UUIDS: %s", instancesList);

        return instancesList;

    ## END INSTANCES.



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
        LOG.info("GET AVALIBLE RESOURCES! NODE %s", nodename);
        
        ## Request to MCT Agent informations about MCT resources. The return is
        ## a dictionary of information resources. These values depend on the di
        ## vision of the player belongs.
        valRet = self.mct.get_resource_inf();

        resources = {};

        ## Convert the units to compreensive format. The original forma is "MB".
        if valRet != {}:
            resources['vcpus'         ] = valRet['data']['vcpu'          ]; 
            resources['vcpus_used'    ] = valRet['data']['vcpu_used'     ]; 
            resources['memory_mb'     ] = valRet['data']['memory_mb'     ];
            resources['memory_mb_used'] = valRet['data']['memory_mb_used'];
            resources['local_gb'      ] = valRet['data']['disk_mb'       ]/1024;
            resources['local_gb_used' ] = valRet['data']['disk_mb_used'  ]/1024;
        else:
            resources['vcpus'         ] = 10; 
            resources['vcpus_used'    ] = 0; 
            resources['memory_mb'     ] = 100000;
            resources['memory_mb_used'] = 0;
            resources['local_gb'      ] = 100000;
            resources['local_gb_used' ] = 0;

        ## Copy the status base (fixed values) and concatenate with actual reso
        ## urce informations obtained from MCT.
        actualResourcesStatus = self.__resourcesStatusBase.copy();
        actualResourcesStatus.update(resources);

        return actualResourcesStatus;


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

        LOG.info("CLEANUP - NOT IMPLEMENTED YET!");
        pass;


    ## ------------------------------------------------------------------------
    ## EXPLICT ACTIONS
    ## ------------------------------------------------------------------------
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

        ## Add an instance in the list: the pwr instance initial is not defined.
        self.__instances.insert(instance, 'BUILDING', power_state.NOSTATE);

        ## Send request to create the remote instance in multicloud tournamment.
        valRet = self.mct.create_instance(data);

        if valRet != {}:
            mState = self.returnState[valRet['status']];
            pState = self.returnState[valRet['status']];
        else:
            mState = MCT_UNREACHABLE;
            pState = self.returnState[0];

        ## Update instance data.
        self.__instances.change_mct_state(instance['uuid'], mState);
        self.__instances.change_pwr_state(instance['uuid'], pState);

        ## LOG:
        LOG.info("[MCT_DRIVE] INSTANCE SPAWN! STATE: %s", str(valRet));


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

        valRet = {};

        ## Create a new dictionary struct with will be contain the parameter to
        ## intance a new VM.
        data = {
            'instance': instance
        }

        ## Get the unique identifier (uuid) belogs the instance to be removed. 
        uuid = instance['uuid'];

        pState = self.__instances.get_pwr_state(uuid); 
        mState = self.__instances.get_mct_state(uuid);

        ## Check if the instance exist:
        if self.__instances.check_exist(uuid) == True:

            ## In both cases (NOSTATE|CRASHED) the vm is not running in the mct.
            if pState != power_state.NOSTATE and pState != power_state.CRASHED:

                ## TODO: pode acontecer q no ato de criar o MCT nao esteja dis-
                ##       ponivel. Caso acontececa o valRet retorna vazio, entao
                ##       nao apaga a vm da lista pq ela ainda esta em execucao.
                ##
                if self.__instances.get_mct_state(uuid) != MCT_UNREACHABLE:
                    valRet = self.mct.delete_instance(data);

        else:
            LOG.warning("INSTANCES uuid=%s NOT IN LOCAL DICTIONARY!", uuid);

        if valRet != {}:
            ## Remove instance from list (check by UUID). Update internal dbase.
            self.__instances.remove(uuid); 

            ## LOG:
            LOG.info("INSTANCE UUID=%s NOT DESTROYED!", uuid);
        else:
            ## LOG:
            LOG.info("INSTANCE UUID=%s YET DESTROYED!", uuid);


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
        ## LOG.
        LOG.info("SNAPSHOT - NOT IMPLEMENTED YET!");
        pass;
         

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

        ## LOG:
        LOG.info("REBOOT - NOT IMPLEMENTED YET!");

        ## After this called successfully, the instance's state goes back to po
        ## wer_state.RUNNING. The virtualization plataform should ensure that t
        ## he reboot action has completed successfully even in cases in which t
        ## he undelying domain/vm is paused or halted/stoped.
        pass;


    ##
    ## BRIEF: soft delete an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM instance == (nova.objects.instance) Instance This function should
    ##                    use the data there to guide the creation of the new
    ##                    instance.
    ##
    def soft_delete(self, instance):
        ## LOG:
        LOG.info("SOFT DELETE INSTANCE - NOT IMPLEMENTED YET!");
        pass


    ##
    ## BRIEF: restore an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM instance == (nova.objects.instance) Instance This function should
    ##                    use the data there to guide the creation of the new
    ##                    instance.
    ##
    def restore(self, instance):
        ## LOG:
        LOG.info("RESTORE INSTANCE - NOT IMPLEMENTED YET!");
        pass


    ##
    ## BRIEF: pause an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM instance == (nova.objects.instance) Instance This function should
    ##                    use the data there to guide the creation of the new
    ##                    instance.
    ##
    def pause(self, instance):
        ## LOG:
        LOG.info("PAUSE INTERFACE - NOT IMPLEMENTED YET!");
        pass


    ##
    ## BRIEF: unpause an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM instance == (nova.objects.instance) Instance This function should
    ##                    use the data there to guide the creation of the new
    ##                    instance.
    ##
    def unpause(self, instance):
        ## LOG:
        LOG.info("UNPAUSE INTERFACE - NOT IMPLEMENTED YET!");
        pass


    ##
    ## BRIEF: suspend an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM instance == (nova.objects.instance) Instance This function should
    ##                    use the data there to guide the creation of the new
    ##                    instance.
    ##
    def suspend(self, instance):
        ## LOG:
        LOG.info("SUSPEND INTERFACE - NOT IMPLEMENTED YET!");
        pass


    ##
    ## BRIEF: power off an instance.
    ## ------------------------------------------------------------------------
    ##
    def power_off(self, instance, shutdown_timeout=0, shutdown_attempts=0):
        ## LOG:
        LOG.info("POWER OFF INTERFACE - NOT IMPLEMENTED YET!");
        pass


    ##
    ## BRIEF: power on an instance.
    ## ------------------------------------------------------------------------
    ##
    def power_on(self, context, instance, network_info, block_device_info):
        ## LOG:
        LOG.info("POWER ON INTERFACE - NOT IMPLEMENTED YET!");
        pass


    ##
    ## BRIEF: resume an instance.
    ## ------------------------------------------------------------------------
    ##
    def resume(self, context, instance, network_info, block_device_info=None):
        ## LOG:
        LOG.info("RESUME INTERFACE - NOT IMPLEMENTED YET!");
        pass

    ## END ACTIONS.


    ## ------------------------------------------------------------------------
    ## VIFS
    ## ------------------------------------------------------------------------
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
        LOG.info("PLUG VIFS - NOT IMPLEMENTED YET!");
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
        LOG.info("UNPLUG VIFS - NOT IMPLEMENTED YET!");
        pass


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def attach_interface(self, instance, image_meta, vif):
        if vif['id'] in self.__interfaces:
            raise exception.InterfaceAttachFailed(
                    instance_uuid=instance['uuid'])
        self.__interfaces[vif['id']] = vif


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def detach_interface(self, instance, vif):
        try:
            del self.__interfaces[vif['id']]
        except KeyError:
            raise exception.InterfaceDetachFailed(
                    instance_uuid=instance['uuid'])
    ## END VIFS.



    ## ------------------------------------------------------------------------
    ## VOLUMES
    ## ------------------------------------------------------------------------
    def get_all_volume_usage(self, context, compute_host_bdms):
        """Return usage info for volumes attached to vms on
           a given host.
        """
        volusage = []
        return volusage


    ##
    ## BRIEF: get the connector information for the instance for attaching to
    ##        volumes. 
    ## ------------------------------------------------------------------------
    ## @PARAM instance ==  
    ##
    def get_volume_connector(self, instance):
        ## LOG:
        LOG.info("[MCT_DRIVE] GET VOLUME CONNECTOR - NOT IMPLEMENTED YET!");

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
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def attach_volume(self, context, connection_info, instance, mountpoint,
                      disk_bus=None, device_type=None, encryption=None):
        """Attach the disk to the instance at mountpoint using info."""
        instance_name = instance['name']
        if instance_name not in self.__mounts:
            self.__mounts[instance_name] = {}
        self.__mounts[instance_name][mountpoint] = connection_info


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def detach_volume(self, connection_info, instance, mountpoint,
                      encryption=None):
        """Detach the disk attached to the instance."""
        try:
            del self.__mounts[instance['name']][mountpoint]
        except KeyError:
            pass


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def swap_volume(self, old_connection_info, new_connection_info,
                    instance, mountpoint, resize_to):
        """Replace the disk attached to the instance."""
        instance_name = instance['name']
        if instance_name not in self.__mounts:
            self.__mounts[instance_name] = {}
        self.__mounts[instance_name][mountpoint] = new_connection_info

    ## END VOLUMES.








    ##
    ## BRIEF: check access of instance files on the host.
    ## ------------------------------------------------------------------------
    ## @PARAM instance == nova.object.instance.Instance to lookup.
    ##
    ## @RETURN (bool) True if files of an instance with the supplied ID accessi
    ##                ble on the host. False otherwise.
    ##
    def instance_on_disk(self, instance):
        ## LOG:
        LOG.info("INSTANCE ON DISK!");

        ## NOTE: used in rebuild for HA implementation and required for valida-
        ##       tion of access to instance shared disk files.
        return False;

    ##
    ## BRIEF: retrieves the IP addres od the dom0.
    ## ------------------------------------------------------------------------
    ##
    @staticmethod
    def get_host_ip_addr():
        LOG.info("get_host_ip_addr!");
        return '192.168.0.1';

    ##
    ## BRIEF: reboot, shutsdown or powers up the host.
    ## ------------------------------------------------------------------------
    ## @PARAM host   == the target.
    ## @PARAM action == the action.
    ##
    def host_power_action(self, host, action):
        LOG.info("HOST POWER ACTION!");
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
        LOG.info("host_maintenance_mode!");

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
        LOG.info("set_host_enable!");

        if enabled:
            return 'enabled';

        return 'disabled';








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










    def get_all_bw_counters(self, instances):
        """Return bandwidth usage counters for each interface on each
           running VM.
        """
        bw = []
        return bw


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
## EOF.
