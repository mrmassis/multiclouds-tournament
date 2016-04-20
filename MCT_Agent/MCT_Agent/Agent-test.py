#!/usr/bin/python

import socket;
import time;
import json;
import ConfigParser;
import requests;


from multiprocessing            import Process, Queue, Lock;
from lib.amqp                   import RabbitMQ_Publish, RabbitMQ_Consume;




###############################################################################
## DEFINITIONS                                                               ## 
###############################################################################
POOLING_TIME_INTERVAL = 5;

ADDR = 'localhost';
PORT = 12345;

CERT_FILE = '';

HEADERS = {'Content-type': 'application/json'};
ADDRESS = 'http://localhost:50000/Authentication';




###############################################################################
## CLASSES                                                                   ## 
###############################################################################
class MCT_Agent:

    """
    ---------------------------------------------------------------------------
    """
    ###########################################################################
    ## ATTRIBUTES                                                            ## 
    ###########################################################################
    __monitorThreads = None;
    __playerToken    = None;
    __cfg            = None;
    __cfgFile        = None;
    __properties     = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ## 
    ###########################################################################
    def __init__(self, cfgFile = '/etc/mct/agent.ini'):


        ## Setup our ssl options
        ##ssl_options = {"cacerts": "/etc/rabbitmq/ssl/testca/cacert.pem",
        ##               "certfile": "/etc/rabbitmq/ssl/client/cert.pem",
        ##               "keyfile": "/etc/rabbitmq/ssl/client/key.pem",
        ##               "cert_reqs": CERT_REQUIRED,
        ##               "verify": "verify_peer",
        ##               "fail_if_no_peer_cert": True}
        ##
        ## Connect to RabbitMQ
        ##connection = SelectConnection(ConnectionParameters(host, 5671),
        ##                              on_connected,
        ##                              ssl=True,
        ##                              ssl_options=ssl_options)


        self.__cfgFile        = cfgFile;
        self.__cfg            = {};
        self.__monitorThreads = {};
        self.__playerToken    = '';

        ## Obtain all configs itens:
        self.__get_config();

        self.__publisher = RabbitMQ_Publish(self.__cfg['amqp']);


    ###########################################################################
    ## PUBLIC METHODS                                                        ## 
    ###########################################################################
    def run(self):
        ## Realiza a autenticacao do player junto ao MCT_Referee e espera um to
        ## ken de autenticacao.
        #idata = self.__cfg['properties'];

        msg = {
            'code'   : 0001,
            'playerId': 'player1',
            'status' : 0,
            'retId'  : '',
            'reqId'  : 'kjfklsajdlkajdlakjdal',
            'origAdd': '10.0.0.30',
            'destAdd': '',
            'data'   : {
             }
        };

        data = {'action': 'create', 'player':'1', 'vmt_id':'B', 'msg_id':'00000001', 'div_id':'1'};
        self.__publisher.publish(msg, self.__cfg['amqp']['route']);

        return 0;



    ###########################################################################
    ## PRIVATE METHODS                                                       ## 
    ###########################################################################
    ##
    ## Brief: inicia um novo monitoramento.
    ## ------------------------------------------------------------------------
    ## @PARAM body == corpo da mensagem recebida.
    ##
    def __add_monitor(self, body):
        uuid = body['uuid'];

        if not self.__monitorThreads.has_key(uuid):
            monitor = Monitor(self.__cfg['monitor'], uuid, self.__playerToken);
            monitor.start();

            self.__monitorThreads[uuid] = monitor;

        return 0;


    ##
    ## Brief: finaliza um monitoramento.
    ## ------------------------------------------------------------------------
    ## @PARAM body == corpo da mensagem recebida.
    ##
    def __del_monitor(self, body):
        uuid = body['uuid'];

        try:
            monitor = self.__monitorThreads.pop(uuid);

            monitor.terminate();
            monitor.join();
        except:
            pass;

        return 0;


    ##
    ## Brief: obtem todas as configuracoes.
    ## ------------------------------------------------------------------------
    ##
    def __get_config(self):
       config = ConfigParser.ConfigParser();
       config.readfp(open(self.__cfgFile));

       ## Varre todo o arquivo de configuracao e obtem as informacoes pertinen-
       ## tes e salva no dicionario cfg.
       for section in config.sections():
           self.__cfg[section] = {};

           for option in config.options(section):
               self.__cfg[section][option] = config.get(section,option);

       return 0;





###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":
    mct_agent = MCT_Agent();
    mct_agent.run();

## EOF.
                                   
