#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
__all__ = ['MCT_Authenticate'];

import socket;
import time;
import json;





###############################################################################
## DEFINITION                                                                ##
###############################################################################
TIME_TO_WAIT = 10
TRIES        = 10





###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Registry(object):

    """
    MCT_Registry perform the register in the tournament.
    ---------------------------------------------------------------------------
    * registry == authenticate a player.
    """

    ###########################################################################
    ## DEFINITION                                                           ##
    ###########################################################################
    __clientName = None;
    __clientAddr = None;
    __serverName = None;
    __serverAddr = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ## @PARAMA dictClient == dictionaty with information about the client.
    ##
    def __init__(self, dictClient):

        self.__dictClient = dictClient;



    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: autheticate the player.
    ## -----------------------------------------------------------------------
    ## 
    def registry(self):
        messageDictRecv = {'status' : 0};
        count = 0;

        addr = self.__dictClient['authenticate_address']; 
        port = self.__dictClient['authenticate_port'];

        while count < TRIES:
            try:
                connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                connection.connect((addr, int(port)));

                messageDictSend = {
                    'code'    : -1,
                    'playerId': self.__dictClient['name'],
                    'status'  : 0,
                    'reqId'   : '',
                    'retId'   : '',
                    'origAddr': self.__dictClient['agent_address'],
                    'destAddr': '',
                    'destName': '',
                    'data'    : {}
                }

                ## Format message to 'json' (convert dictionary to json format):
                messageJsonSend=json.dumps(messageDictSend, ensure_ascii=False); 

                ## Send the message to the MultiClouds Tournament referee. After
                ## wait by the return:
                connection.sendall(messageJsonSend);

                ## Wait the response from MCT server and convert the json messa
                ## ge to the python dictionary format.
                messageJsonRecv = connection.recv(1024);
                
                messageDictRecv = json.loads(messageJsonRecv);

                connection.close();
                break;

            except:
                pass;

            time.sleep(TIME_TO_WAIT);
            count += 1;

        return int(messageDictRecv['status']), messageDictRecv['data']['token'];
## END CLASS;








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    sAddr = '10.3.77.156';
    sPort = '2000'; 

    cName = 'vPlayer0';
    cAddr = '10.3.77.162'

    mct_registry = MCT_Registry(cAddr, cName, sAddr, sPort);
    mct_registry.registry();

## END.

