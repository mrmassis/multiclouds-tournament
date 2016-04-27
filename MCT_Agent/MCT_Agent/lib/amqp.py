#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
import json;
import pika;





###############################################################################
## DEFINITION                                                                ##
###############################################################################
DELIVERY_MODE = 2;
EXCHANGE_TYPE = 'direct';



###############################################################################
## PROCEDURES                                                                ##
###############################################################################
class RabbitMQ_Publish(object):

    """
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## DEFINITION                                                           ##
    ###########################################################################
    __host     = None;
    __exchange = None;
    __appId    = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, data):

        self.__identifier = data['identifier'];
        self.__exchange   = data['exchange'  ];
        self.__address    = data['address'   ]

        ## Connection parameters object that is passed into the connection ada-
        ## pter upon construction. 
        parameters = pika.ConnectionParameters(host=self.__address);

        ## The BlockingConnection creates a layer on top of Pika's asynchronous
        ## core providing methods that will block until their expected response
        ## has returned. Due to the asynchronous nature of the Basic.Deliver a-
        ## nd Basic.Return calls from RabbitMQ to your application, you can st-
        ## ill implement continuation-passing style asynchronous methods if yo-
        ## u'd like to receive messages from RabbitMQ using basic_consume or if
        ## you want to be notified of a delivery failure when using basic_publ-
        ## ish . 
        connection = pika.BlockingConnection(parameters);

        ## Create a new channel with the next available channel number or pass
        ## in a channel number to use. Must be non-zero if you would like to s-
        ## pecify but it is recommended that you let Pika manage the channel n-
        ## umbers.
        self.__chn = connection.channel();

        ## This method creates an exchange if it does not already exist, and if
        ## the exchange exists, verifies that it is of the correct and expected
        ## class.
        self.__chn.exchange_declare(exchange=self.__exchange,type=EXCHANGE_TYPE);
 
        ##
        self.__chn.confirm_delivery;



    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM body == 
    ##
    def publish(self, body, rKey):
        ##
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
        ack = self.__chn.basic_publish(self.__exchange, rKey, jData, properties);

        return ack;
## END.








class RabbitMQ_Consume(object):

    """
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, data):

        qName    = data['queue_name'];
        rKey     = data['route'     ];
        address  = data['address'   ];
        exchange = data['exchange'  ];

        ## Connection parameters object that is passed into the connection ada-
        ## pter upon construction. 
        parameters = pika.ConnectionParameters(host=address);

        ## The BlockingConnection creates a layer on top of Pika's asynchronous
        ## core providing methods that will block until their expected response
        ## has returned. Due to the asynchronous nature of the Basic.Deliver a-
        ## nd Basic.Return calls from RabbitMQ to your application, you can st-
        ## ill implement continuation-passing style asynchronous methods if yo-
        ## u'd like to receive messages from RabbitMQ using basic_consume or if
        ## you want to be notified of a delivery failure when using basic_publ-
        ## ish . 
        connection = pika.BlockingConnection(parameters);

        ## Create a new channel with the next available channel number or pass
        ## in a channel number to use. Must be non-zero if you would like to s-
        ## pecify but it is recommended that you let Pika manage the channel n-
        ## umbers.
        self.chn = connection.channel();

        ## This method creates an exchange if it does not already exist, and if
        ## the exchange exists, verifies that it is of the correct and expected
        ## class.
        self.chn.exchange_declare(exchange=exchange, type='direct');

        ## Declare queue, create if needed. This method creates or checks a qu-
        ## eue. When creating a new queue the client can specify various prope-
        ## rties that control the durability of the queue and its contents, and
        ## the level of sharing for the queue.
        result       = self.chn.queue_declare(queue=qName, durable=True);
        self.__qName = result.method.queue;

        ## Bind the queue to the specified exchange:
        self.chn.queue_bind(exchange=exchange,queue=qName,routing_key=rKey);

        ## Specify quality of service. This method requests a specific quality
        ## of service. The QoS can be specified for the current channel or for
        ## all channels on the connection. The client can request that messages
        ## be sent in advance so that when the client finishes processing a me-
        ## ssage, the following message is already held locally, rather than n-
        ## eeding to be sent down the channel. Prefetching gives a performance
        ## improvement.
        self.chn.basic_qos(prefetch_count=1);

        

    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ##
    def consume(self):
        ## Sends the AMQP command Basic. Consume to the broker and binds messa-
        ## ges for the consumer_tag to the consumer callback. If you do not pa-
        ## ss in a consumer_tag, one will be automatically generated for you.R-
        ## eturns the consumer tag.
        self.chn.basic_consume(self.callback, self.__qName, no_ack=False);

        ## Processes I/O events and dispatches timers and basic_consume callba-
        ## cks until all consumers are cancelled.
        self.chn.start_consuming();


    ##
    ## BRIEF:
    ## ------------------------------------------------------------------------
    ## @PARAM channel    == 
    ## @PARAM method     == 
    ## @PARAM properties == 
    ## @PARAM body       == 
    ##
    def callback(self, channel, method, properties, body):
        return 0;
## EOF.

