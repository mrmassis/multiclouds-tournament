#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
import logging;
import json;
import pika;
import time;

from .utils import *;




###############################################################################
## DEFINITION                                                                ##
###############################################################################
DELIVERY_MODE = 2;
EXCHANGE_TYPE = 'direct';




###############################################################################
## LOG CONFIGURATION                                                         ##
###############################################################################
## Get the name from who caller this package. So the name from caller file must
## be the same of the class inside file.
## caller (deep 2) -> amqp (deep 1) -> utils (deep 0).
logName = get_class_name_from_frame(deep=2);

LOG = logging.getLogger(logName);




###############################################################################
## PROCEDURES                                                                ##
###############################################################################
class RabbitMQ_Publish(object):

    """
    CLASS: RabbitMQ_Publish
    ---------------------------------------------------------------------------
    ** publish == publish assynchronous message by AMQP server.
    """

    ###########################################################################
    ## DEFINITION                                                            ##
    ###########################################################################
    __host       = None;
    __exchange   = None;
    __appId      = None;
    __connection = None;
    __identifier = None;
    __data       = {};


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, data):
        self.__data = data;


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: publish a message (body) in AMQP server.
    ## ------------------------------------------------------------------------
    ## @PARAM body == message to publish.
    ## @PARAM rKey == the route to use. 
    ##
    def publish(self, body, rKey):

        ## Check if the connection is closed or open.To continue the connection
        ## must be open.
        if self.__connect() == False:
            return False;
 
        ## Define some parameter to send the message by the channel. Type of de
        ## livery, app ID, and others.
        properties = pika.BasicProperties(delivery_mode= DELIVERY_MODE,
                                          app_id       = self.__identifier,
                                          content_type = 'application/json',
                                          headers      = body);

        ## Serialize object to a JSON formatted str using this conversion table
        ## If ensure_ascii is False, the result may contain non-ASCII characte-
        ## rs and the return value may be a unicode instance.
        jData = json.dumps(body, ensure_ascii=False);

        ## Publish to the channel with the given exchange,routing key and body.
        ## Returns a boolean value indicating the success of the operation.
        ack = self.__chn.basic_publish(self.__exchange, rKey, jData,properties);

        return True;

   
    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: connect to amqp server.
    ## ------------------------------------------------------------------------
    ##
    def __connect(self):
        
        self.__identifier = self.__data['identifier'];
        self.__exchange   = self.__data['exchange'  ];
 
        addr = self.__data['address'];
        user = self.__data['user'   ];
        pswd = self.__data['pass'   ];

        ## LOG:
        LOG.info('PUBLISH - TRY TO CONNECT (AMQP SERVER) ...');

        try:
           ## Credentials:
           creds = pika.PlainCredentials(user, pswd);

           ## Connection parameters object that is passed into the connection a
           ## dapter upon construction. 
           parameters = pika.ConnectionParameters(host=addr,credentials=creds);

           ## The BlockingConnection creates a layer on top of Pika's asynchron
           ## ous core providing methods that will block until their expected r
           ## esponse ihas returned. Due to the asynchronous nature of the Basi
           ## c.Deliver and Basic. Return calls from RabbitMQ to your applicati
           ## on, you can still implement continuation-passing style asynchrono
           ## us methods if youi had like to receive messages from RabbitMQ usi
           ## ng basic_consume or if you want to be not ified of a delivery fai
           ## lure when using basic_publish . 
           self.__connection = pika.BlockingConnection(parameters);

           ## Create a new channel with the next available channel number or pa
           ## ssin a channel number to use.Must be non-zero if you would like t
           ## o specify but it is recommended that you let Pika manage the chan
           ## nel numbers.
           self.__chn = self.__connection.channel();

           ## This method creates an exchange if it does not already exist, and
           ## if the exchange exists, verifies that it is of the correct and ex
           ## pected class.
           self.__chn.exchange_declare(exchange = self.__exchange,
                                       type     = EXCHANGE_TYPE);

           self.__chn.confirm_delivery;

        except pika.exceptions.AMQPConnectionError:
            ## LOG:
            LOG.error('AMQP CONNECTION ERROR (IS RABBITMQ RUNNING?)!');
            return False;

        except pika.exceptions.AuthenticationError:
            ## LOG:
            LOG.error('AMQP AUTHENTICATION ERROR!');
            return False;

        except:
            ## LOG:
            LOG.error('UNKNOW ERROR!');
            return False;

        ## LOG:
        LOG.info('SUCESS!');
        return True;

## END.








class RabbitMQ_Consume(object):

    """
    CLASS: RabbitMQ_Consume
    ---------------------------------------------------------------------------
    ** consume  == consume message from AMQP server.
    ** callback == method call by de pika when arrive the message (stumb).
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __data       = {};
    __qName      = None;
    __connection = None;
    __chn        = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, data):

        self.__data = data;

        ## Try estabelish the connection with the AMQP server.
        self.__connect();


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: stat the consume messagem process.
    ## ------------------------------------------------------------------------
    ##
    def consume(self):

        while True:
            ## Sends the AMQP command Basic. Consume to the broker and binds me
            ## ssages for the consumer_tag to the consumer callback.If you do n
            ## ot pass in a consumer_tag, one will be automatically generated f
            ## or you. Returns the consumer tag.
            self.chn.basic_consume(self.callback, self.__qName, no_ack=False);

            ## Processes I/O events and dispatches timers and basic_consume cal
            ## lbacks until all consumers are cancelled.
            try:
                self.chn.start_consuming();

            except pika.exceptions.ConnectionClosed:
                ## LOG:
                LOG.info('CONNECTION LOST! RECONNECT...');
                self.__connect();
            

    ##
    ## BRIEF: callback prototype.
    ## ------------------------------------------------------------------------
    ## @PARAM channel    == 
    ## @PARAM method     == 
    ## @PARAM properties == 
    ## @PARAM body       == 
    ##
    def callback(self, channel, method, properties, body):
        return 0;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: connect to amqp server.
    ## ------------------------------------------------------------------------
    ##
    def __connect(self):

        qNme = self.__data['queue_name'];
        rKey = self.__data['route'     ];
        addr = self.__data['address'   ];
        exch = self.__data['exchange'  ];

        while True:
            ## LOG:
            LOG.info('CONSUME - TRY TO CONNECT (AMQP SERVER) ...');

            try:
                ## Credentials:
                ## credentials=pika.PlainCredentials(data['user'],data['pass']);

                ## Connection parameters object that is passed into the connect
                ## ion dapter upon construction. 
                parameters = pika.ConnectionParameters(host=addr);

                ## Creates a layer on top of Pika's asynchronous core providing
                ## methods that will block until their expected response has re
                ## turned. Due to the asynchronous nature of the Basic.Deliver,
                ## and Basic.Return calls from RabbitMQ to your application, yo
                ## u can still implement continuation-passing style asynchronou
                ## s methods if you'd like to receive messages from RabbitMQ us
                ## ing basic_consume or if you want to be notified of a deliver
                ## y failure when using basic_publish. 
                self.__connection = pika.BlockingConnection(parameters);

                ## Create a new channel with the next available channel numb. o
                ## r pass in a channel number to use. Must be non-zero if you w
                ## ould like to specify but it is recommended that you let Pika
                ##  manage the channel numbers.
                self.chn = self.__connection.channel();

                ## This method creates an exchange if it does not already exist
                ## i, and if the exchange exists, verifies that it is of the co
                ## rrect and expected class.
                self.chn.exchange_declare(exchange=exch, type='direct');

                ## Declare queue,create if needed.This method creates or checks
                ## a queue. When creating a new queue the client can specify va
                ## rious properties that control the durability of the queue an
                ## d its contents, and the level of sharing for the queue.
                result       = self.chn.queue_declare(queue=qNme,durable=True);
                self.__qName = result.method.queue;

                ## Bind the queue to the specified exchange:
                self.chn.queue_bind(exchange=exch,queue=qNme,routing_key=rKey);

                ## Specify quality of service.This method requests a specific q
                ## uality of service.The QoS can be specified for the current c
                ## hannel or for all channels on the connection. The client can
                ## request that messages be sent in advance so that when the cl
                ## ient finishes processing a message, the following message is
                ## already held locally, rather than needing to be sent down th
                ## e channel. Prefetching gives a performance improvement.
                self.chn.basic_qos(prefetch_count=1);
                break;

            except pika.exceptions.AMQPConnectionError:
                ## LOG:
                LOG.error('AMQP CONNECTION ERROR (IS RABBITMQ RUNNING?)!');

            except pika.exceptions.AuthenticationError:
                ## LOG:
                LOG.error('AMQP AUTHENTICATION ERROR!');

            except:
                ## LOG:
                LOG.error('UNKNOW ERROR!');

            ## LOG:
            LOG.error('FAIL! TRY AGAIN!');

            ## Wait 10 seconds to try again!
            time.sleep(10);

        ## LOG:
        LOG.info('SUCESS!');
        return True;
## EOF.

