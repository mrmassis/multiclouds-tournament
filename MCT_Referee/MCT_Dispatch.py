#!/usr/bin/env python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
import sys;
import json;
import datetime;
import logging;
import logging.handlers;
import os;

from sqlalchemy                  import and_, or_;
from mct.lib.utils               import *;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy,Request,Player;
from mct.lib.amqp                import RabbitMQ_Publish, RabbitMQ_Consume;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE           = 'mct-dispatch.ini';
HOME_FOLDER           = os.path.join(os.environ['HOME'], CONFIG_FILE);
RUNNING_FOLDER        = os.path.join('./'              , CONFIG_FILE);
DEFAULT_CONFIG_FOLDER = os.path.join('/etc/mct/'       , CONFIG_FILE);
AGENT_ROUTE           = 'mct_agent';
AGENT_IDENTIFIER      = 'MCT_Dispatch';
AGENT_EXCHANGE        = 'mct_exchange';
AGENT_QUEUE           = 'agent';








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Dispatch(RabbitMQ_Consume):

    """
    Dispatch to appropriate destinations requires received from players or divi
    sions.
    ---------------------------------------------------------------------------
    ** callback == method invoked when the pika receive a message.
    ** stop     == consume stop.    
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __publish_referee = None;
    __publish_register= None;
    __divisions       = [];
    __configs         = None;
    __dbConnection    = None;
    __rabbitUser      = None;
    __rabbitPass      = None;
    __print           = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM dict cfg    == dictionary with configurations about MCT_Agent.
    ## @PARAM obj  logger == logger object.
    ##
    def __init__(self, cfg, logger):

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## Get which 'route' is used to deliver the message to the MCT_Referee
        ## and MCT_Register:
        self.__routeReferee = cfg['amqp_publish_referee' ]['route'];
        self.__routeRegister= cfg['amqp_publish_register']['route'];

        ## Get password used to publish message to player (regular or virtual)
        self.__rabbitUser   = cfg['amqp_publish_players']['user' ];
        self.__rabbitPass   = cfg['amqp_publish_players']['pass' ];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, cfg['amqp_consume']);

        ## Instance a new object to perform the publication of 'AMQP' messages.
        self.__publish_referee =RabbitMQ_Publish(cfg['amqp_publish_referee' ]);
        self.__publish_register=RabbitMQ_Publish(cfg['amqp_publish_register']);

        ## Intance a new object to handler all operation in the local database.
        self.__db = MCT_Database_SQLAlchemy(cfg['database']);

        ## LOG:
        self.__print.show("###### START MCT_DISPATCH ######\n",'I');


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: method invoked when the pika receive a message.
    ## ------------------------------------------------------------------------
    ## @PARAM pika.Channel              channel    = the communication channel.
    ## @PARAM pika.spec.Basic.Deliver   method     = 
    ## @PARAM pika.spec.BasicProperties properties = 
    ## @PARAM str                       message    = message received.
    ##
    def callback(self, channel, method, properties, msg):

        ## Send to source an ack msg to ensuring that the message was received.
        self.chn.basic_ack(method.delivery_tag);

        msg = json.loads(msg);

        ## LOG:
        self.__print.show('MSG RECEIVED: ' + str(msg['code']), 'I');

        ## Check if is a request received from players or a return from a divi-
        ## sions. The identifier is the properties.app_id.
        if   properties.app_id == 'MCT_Referee' :
            self.__recv_message_from_referee(msg, properties.app_id);

        elif properties.app_id == 'MCT_Register':
            self.__recv_message_from_register(msg,properties.app_id);

        else:
            self.__recv_message_from_players(msg, properties.app_id);

        ## LOG:
        self.__print.show('------------------------------------------\n', 'I');
        return 0;


    ##
    ## BRIEF: consume stop.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        self.chn.basic_cancel(self.consumeTag);
        self.chn.close();
        self.connection.close();

        ## LOG:
        self.__print.show("###### STOP MCT_DISPATCH ######\n",'I');
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: receive message from referee.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg   == received message.
    ## @PARAM str  appId == source app id.
    ##
    def __recv_message_from_referee(self, msg, appId):

        ## LOG:
        self.__print.show('MESSAGE RETURNED OF REFEREE: ' + str(msg), 'I');

        ## If status is equal the 'MESSAGE_PARSE_ERROR' the request had fields
        ## missed.
        if msg['status'] != MESSAGE_PARSE_ERROR:

            if msg['retId'] == '':

                ## Remove the message (put previous) in the pending requests di
                ## ctionary.
                valRet = self.__remove_query(msg['reqId'], msg['playerId']);

                playerAddress = msg['origAddr'];

            ## Make the request forward to player that will accept the request.
            else:
                playerAddress = msg['destAddr'];

            ## Create the configuration about the return message.This configura
            ## tion will be used to send the messagem to apropriate player.
            config = {
                'identifier': AGENT_IDENTIFIER,
                'route'     : AGENT_ROUTE,
                'exchange'  : AGENT_EXCHANGE,
                'queue_name': AGENT_QUEUE,
                'address'   : playerAddress,
                'user'      : self.__rabbitUser,
                'pass'      : self.__rabbitPass
            };

            targetPublish = RabbitMQ_Publish(config); 
            targetPublish.publish(msg, AGENT_ROUTE);

            del targetPublish;

        return 0;


    ##
    ## BRIEF: receive message from register.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg   == received message.
    ## @PARAM str  appId == source app id.
    ##
    def __recv_message_from_register(self, msg, appId):

        ## LOG:
        self.__print.show('MESSAGE RETURNED OF REGISTER: ' + str(msg), 'I');

        ## Set the agent address. 
        playerAddress = msg['origAddr'];

        ## Create the configuration about the return message.This configuration
        ## will be used to send the messagem to apropriate player.
        config = {
            'identifier': AGENT_IDENTIFIER,
            'route'     : AGENT_ROUTE,
            'exchange'  : AGENT_EXCHANGE,
            'queue_name': AGENT_QUEUE,
            'address'   : playerAddress,
            'user'      : self.__rabbitUser,
            'pass'      : self.__rabbitPass
        };

        targetPublish = RabbitMQ_Publish(config);
        targetPublish.publish(msg, AGENT_ROUTE);

        del targetPublish;

        return 0;


    ##
    ## BRIEF: send message to the refereee.
    ## ------------------------------------------------------------------------
    ## @PARAM dict msg   == received message.
    ## @PARAM str  appId == source app id.
    ##
    def __recv_message_from_players(self, msg, appId):

       ## LOG:
       self.__print.show('RECV FROM PLAYER ' + str(msg)+ ' APPID ' +appId,'I');

       ## These two actions described above is executed by MCT_Register module.
       if   msg['code'] == ADD_REG_PLAYER or msg['code'] == DEL_REG_PLAYER:
               self.__publish_register.publish(msg, self.__routeRegister);
       else:
           ## Check if the player has access to tournament:
           valid = self.__valid_action_player(msg);

           if valid == True:

               ## Adds the message in the pending requests dictionary.If its al
               ## ready inserted does not perform the action.
               self.__append_query(msg['playerId'], msg['reqId'], msg['code']);

               ## LOG:
               self.__print.show('MSG SEND TO REFEREE: '+str(msg), 'I');

               ## Send msg to referee.
               self.__publish_referee.publish(msg, self.__routeReferee);

       return 0;


    ##
    ## BRIEF: valid the action (security).
    ## -------------------------------------------------------------------------
    ## @PARAM msg == received message.
    ##
    def __valid_action_player(self, msg):
        ## LOG:
        self.__print.show('VALID THE ACTION: ' + str(msg), 'I');

        ## Get information about the player.
        dRecv=self.__db.all_regs_filter(Player,(Player.name == msg['playerId']));

        if dRecv != []:

            ## Verify if the player is enabled and the token received is valid. 
            if dRecv[-1]['enabled'] == '1': 
                ## LOG:
                self.__print.show('PLAYER VALID: ' + str(msg), 'I');
                return True;

        ## LOG:
        self.__print.show('PLAYER NOT VALID TO EXECUTE ACTION: '+str(msg), 'I');
        return False;


    ##
    ## BRIEF: stores the request identifier.
    ## ------------------------------------------------------------------------
    ## @PARAM str playerId  == identifier of the player.
    ## @PARAM str requestId == identifier of the request.
    ## @PARAM str actionId  == identifier of the action.
    ##
    def __append_query(self, playerId, requestId, actionId):
        ## Get timestamp: 
        timeStamp = timeStamp = str(datetime.datetime.now());

        ## Check if the line that represent the request already in db. Perform
        ## a select.
        fColumns = and_(Request.request_id == requestId,
                        Request.player_id  == playerId);

        ##
        dReceived = self.__db.all_regs_filter(Request, fColumns);

        ## Verifies that the request already present in the requests 'database'
        ## if not insert it. The second clause meaning the requests id repeat.
        if dReceived == [] or dReceived[-1]['status'] != 0:

            ## LOG:
            self.__print.show('MESSAGE PENDING ' + requestId, 'I');

            ## Insert a line in table REQUEST from database mct. Each line mean
            ## a request finished or in execution.
            request = Request();

            request.player_id          = playerId;
            request.request_id         = requestId;
            request.action             = actionId;
            request.status             = 0;
            request.timestamp_received = timeStamp;

            valRet = self.__db.insert_reg(request);
            return 0;

        ## LOG:
        self.__print.show('MESSAGE ALREADY PENDING ' + requestId, 'I');
        return 1;


    ##
    ## BRIEF: remove the request identifier.
    ## ------------------------------------------------------------------------
    ## @PARAM str playerId  == identifier of the player.
    ## @PARAM str msgId == identifier of the request.
    ##
    def __remove_query(self, playerId, requestId):
        ## Obtain the finish timestamp. 
        timeStamp = timeStamp = str(datetime.datetime.now());

        ## Filter to update:
        fColumns = and_(Request.request_id == requestId,
                        Request.player_id  == playerId);

        fieldsToUpdate = {
            'status'             : 1,
            'timestamp_finished' : timeStamp,
        };

        ## Update the base.
        valRet=self.__db.update_reg(Request, fColumns, fieldsToUpdate);
 
        ## LOG:
        self.__print.show('MESSAGE '+requestId+' REMOVED FROM PENDING!', 'I');
        return 0;
## END CLASS.








class Main:

    """
    Class Main: main class.
    --------------------------------------------------------------------------
    PUBLIC METHODS:
    ** start == start the process.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __cfg     = None;
    __logger  = None;
    __print   = None;
    __running = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: iniatialize the object.
    ## ------------------------------------------------------------------------
    ##
    def __init__(self):

        ## Get the configurantion parameters.
        self.__cfg    = self.__get_configs();

        ## Configurate the logger. Use the parameters defineds in configuration
        ## file.
        self.__logger = self.__logger_setting(self.__cfg['log']);


    ###########################################################################
    ## PUBLIC                                                                ##
    ###########################################################################
    ##
    ## BRIEF: start the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def start(self):
        self.__running = MCT_Dispatch(self.__cfg, self.__logger);
        self.__running.consume();
        return 0;


    ##
    ## BRIEF: stiop the MCT_DB_Proxy.
    ## ------------------------------------------------------------------------
    ##
    def stop(self):
        self.__running.stop();
        return 0;


    ###########################################################################
    ## PRIVATE                                                               ##
    ###########################################################################
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
