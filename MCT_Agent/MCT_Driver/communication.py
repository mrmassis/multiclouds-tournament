#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
import ConfigParser;
import json;
import pika;
import logging;

from multiprocessing     import Process
from nova.virt.mct.utils import *;
from pika.exceptions     import AMQPConnectionError, AMQPChannelError;






###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CONFIG_FILE = '/etc/mct/mct_drive.ini';

LOG = logging.getLogger(__name__);




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
        self.__config = get_configs(CONFIG_FILE);

        ## Intance a new object to handler all operation in the local database
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
        query = "INSERT INTO REQUEST (request_id, status, message) VALUES (%s,%s,%s)";
        value = (message['reqId'], message['status'], str(message['data']));
       
        valret = self.__dbConnection.insert_query(query, value);
 
        LOG.info(valret);


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

        ## Publish to the channel with the given exchange,routing key and body.
        ## Returns a boolean value indicating the success of the operation.
        try:
            exchange = self.__config['amqp_publish']['exchange'];
            route    = self.__config['amqp_publish']['route'   ];

            ack = self.chnP.basic_publish(exchange, route, jData, properties);

        except (AMQPConnectionError, AMQPChannelError), error:
            ack = -1; 

        return ack;


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

        ## TODO:
        ## check close callbacks:

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

        ## Credentials:
        user = self.__config['rabbitmq']['user'];
        pswd = self.__config['rabbitmq']['pass'];

        credentials = pika.PlainCredentials(user, pswd);

        ## Connection parameters object that is passed into the connection ada-
        ## pter upon construction. 
        parameters = pika.ConnectionParameters(host        = cfg['address'],
                                               credentials = credentials);

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
## EOF.
