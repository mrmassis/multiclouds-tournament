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
import hashlib;

from mct.lib.utils               import *;
from mct.lib.database_sqlalchemy import MCT_Database_SQLAlchemy, Player;
from mct.lib.amqp                import RabbitMQ_Publish, RabbitMQ_Consume;








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE           = 'mct-register.ini';
HOME_FOLDER           = os.path.join(os.environ['HOME'], CONFIG_FILE);
RUNNING_FOLDER        = os.path.join('./'              , CONFIG_FILE);
DEFAULT_CONFIG_FOLDER = os.path.join('/etc/mct/'       , CONFIG_FILE);








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Register(RabbitMQ_Consume):

    """
    CLASS MCT_Register: register the new player in the bollentin.
    ---------------------------------------------------------------------------
    ** callback == wait for new request to player register.
    ** stop     == consume stop.    

    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __addr           = None;
    __port           = None;
    __db             = None;
    __print          = None;
    __accessDivision = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAM cfg    == dictionary with configurations about MCT_Agent.
    ## @PARAM logger == logger object.
    ##
    def __init__(self, cfg, logger):

        ## Get the option that define to where the logs will are sent to show.
        self.__print = Show_Actions(cfg['main']['print'], logger);

        ## Get which 'route' is used to deliver the message to the MCT_Referee
        ## and credentials:
        self.__route      = cfg['amqp_publish']['route'];
        self.__rabbitUser = cfg['amqp_publish']['user' ];
        self.__rabbitPass = cfg['amqp_publish']['pass' ];

        ## Initialize the inherited class RabbitMQ_Consume with the parameters
        ## defined in the configuration file.
        RabbitMQ_Consume.__init__(self, cfg['amqp_consume']);

        ## Instance a new object to perform the publication of 'AMQP' messages.
        self.__publish=RabbitMQ_Publish(cfg['amqp_publish']);

        ## Intance a new object to handler all operation in the local database.
        self.__db = MCT_Database_SQLAlchemy(cfg['database']);

        ## Obtain the access division:
        self.__accessDivision = cfg['main']['access_division'];

        ## LOG:
        self.__print.show("###### START MCT_REGISTER ######\n",'I');


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
        self.__print.show('MSG RECEIVED FROM DISPATCH: '+str(msg['code']), 'I');

        if   msg['code'] == ADD_REG_PLAYER:
            msg = self.__authenticates(msg);

        elif msg['code'] == SUS_REG_PLAYER:
            msg = self.__suspendplayer(msg);

        elif msg['code'] == DEL_REG_PLAYER:
            msg = self.__remove_player(msg);

        ## Send the message to MCT_Referee.
        self.__publish.publish(msg, self.__route);

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
        self.__print.show("###### STOP MCT_REGISTER ######\n",'I');
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: receive message from players.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __authenticates(self, msg):
       valRet = FAILED;

       if msg != {}:
           ## Check if the player always registered in the BID. If already reg
           ## ister return the token.
           token = self.__check_player(msg['playerId']);

           if token != '':
               valRet, msg = self.__activate_player(msg, token);
           else:
               valRet, msg = self.__register_player(msg, token);
       
       ## Set the status!    
       msg['status'] = valRet;

       ## LOG:
       self.__print.show('PLAYER REGISTERED: ' + msg['playerId'], 'I');
       return msg;


    ##
    ## BRIEF: suspend player from MCT.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __suspendplayer(self, msg):
        ## Timestamp:
        timeStamp = str(datetime.datetime.now()); 

        ## Set all data to update.
        data = {
            'enabled' : 0,
            'suspend' : timeStamp
        };

        self.__db.update_reg(Player, Player.name == msg['playerId'], data);

        ## LOG:
        self.__print.show('PLAYER SUSPENDED: ' + msg['playerId'], 'I');
        return msg;


    ##
    ## BRIEF: remove player from MCT.
    ## ------------------------------------------------------------------------
    ## @PARAM dict message == received message.
    ##
    def __remove_player(self, msg):
        msg = {};

        ## LOG:
        self.__print.show('PLAYER REMOVED: ' + msg['playerId'], 'I');
        return msg;


    ##
    ## BRIEF: check if the player exist in database.
    ## ------------------------------------------------------------------------
    ## @PARAM str playerId  == identifier of the player.
    ##
    def __check_player(self, playerId):

        ## Check if the line that represent the request already in db. Perform
        ## a select.
        filterRules = {0 : Player.name == playerId};

        ## Check if is possible create the new server (vcpu, memory, and disk).
        dReceived = self.__db.first_reg_filter(Player, filterRules);

        ## Verifies that the request already present in the requests 'database'
        ## if not insert it.
        if dReceived == []:
            ## LOG:
            self.__print.show('PLAYER ID NOT REGISTERED: '+str(playerId), 'I');
            token  = '';

        else:
            ## LOG:
            self.__print.show('PLAYER ID YET REGISTERED: '+str(playerId), 'I');
            token  = dReceived[0]['token'];

        return token;


    ##
    ## BRIEF: register a player in de bid.
    ## ------------------------------------------------------------------------
    ## @PARAM msg   == message received.
    ## @PARAM token == player token ID.
    ##
    def __register_player(self, msg, token):

        ## Calculate initial atts (score|history) to a new player in the MCT.
        iScore, iHistory = self.__initial_attributes(msg['playerId']);

        ## Create the token:
        token = self.__generate_new_token();

        player = Player();

        player.name     = msg['playerId'];
        player.address  = msg['origAddr'];
        player.division = self.__accessDivision;
        player.score    = iScore;
        player.history  = iHistory;
        player.token    = token;
        player.enabled  = 1;

        self.__db.insert_reg(player);

        ## Set the player's token. It will be used in the future to enable the
        ## player actions.
        msg['data']['token'] = token;

        return SUCCESS, msg;


    ##
    ## BRIEF: register a player in de bid.
    ## ------------------------------------------------------------------------
    ## @PARAM msg   == message received.
    ## @PARAM token == player token ID.
    ##
    def __activate_player(self, msg, token):

        ## Set all data to update.
        data = {
            'enabled' : 1
        };

        self.__db.update_reg(Player, Player.name == msg['playerId'], data);

        ## Set the player's token. It will be used in the future to enable the
        ## player actions.
        msg['data']['token'] = token;

        return SUCCESS, msg;


    ##
    ## BRIEF: create a new token.
    ## ------------------------------------------------------------------------
    ##
    def __generate_new_token(self):

        ## Generate a 128 bytes (40 character) safe token.
        token = hashlib.sha1(os.urandom(128)).hexdigest();
        return token;


    ##
    ## BRIEF: calcule the initial attributes to a new players..
    ## ------------------------------------------------------------------------
    ## @PARAM playerId == player identifier.
    ##
    def __initial_attributes(self, playerId):

        ## Calcule the initials attributes to a new player.
        score   = 0.0;
        history = 0;

        return score, history;
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
        self.__running = MCT_Register(self.__cfg, self.__logger);
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
