#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
__all__ = ['MCT_Instances'];

import os;
import time;
import sys;

from mct.lib.utils import *;









###############################################################################
## DESCRIPTION                                                               ##
###############################################################################








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Instances:

    """
    Class MCT_Instances - maitain the state of instances in agent.
    ---------------------------------------------------------------------------
    PUBLIC METHODS
    ** check  == check if the instance exist. 
    ** insert == insert an instance in dicitionary.
    ** remove == remove an instance from structure.
    ** flavor == return flavor ID from a instance.
    ** update == update an instance in dicitionary.
    ** show   == show all instances in structure.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __instances = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):
        self.__instances = {};


    ###########################################################################
    ## PUBLIC METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: check instance status.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def check_instance(self, msg):

        playerSrc = msg['data']['origName'];
        requestId = msg['data']['origId'  ];

        ## If the reqId in dictionary means that the instance was created and
        ## is running. 
        for player in self.__instances.keys():
            if requestId in self.__instances[player]:
                if self.__instances[player][requestId]['status'] == 'running':
                    return SUCCESS;
                else:
                    return FAILED;

        return FAILED;


    ##
    ## BRIEF: insert an instance in dicitionary.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def add_instance(self, msg):
 
        playerSrc = msg['playerId'];
        requestId = msg['reqId'   ];

        ## Check if the instance already running:
        for player in self.__instances.keys():
            if requestId in self.__instances[player]:
                if self.__instances[player][requestId]['status'] != 'failed':
                    return FAILED;

        ## Check if the player that will be receive the request already in the
        ## dictionary.
        if not playerSrc in self.__instances:
            self.__instances[playerSrc] = {}

        ## Insert the new request instance in dictionary and set the state to
        ## pendfing.
        self.__instances[playerSrc][requestId] = {
            'flavor' : msg['data']['flavor'],
            'guest'  : '',
            'status' : 'pendding'
        }

        return SUCCESS;


    ##
    ## BRIEF: change status to finished.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def del_instance(self, msg):
        playerOrign = msg['playerId'];

        ## Change status to finished:
        self.__instances[playerOrign].pop(msg['reqId']);
        return SUCCESS;


    ##
    ## BRIEF: update an instance in dicitionary.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def upd_instance(self, msg):

        playerOrign = msg['playerId'];
        playerGuest = msg['destName'];

        status = 'failed';

        if msg['status'] == SUCCESS:
            self.__instances[playerOrign][msg['reqId']]['guest'] = playerGuest;
            status = 'running';
        
        self.__instances[playerOrign][msg['reqId']]['status' ] = status;
        return SUCCESS;


    ##
    ## BRIEF: return flavor id from an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def get_flavor(self, msg):
        playerOrign = msg['playerId'];

        ## Get flavor ID:
        flavorId = self.__instances[playerOrign][msg['reqId']]['flavor'];

        ## Get the index of the flavor identify:
        idx = FLV_NAME.keys()[FLV_NAME.values().index(flavorId)];

        return idx;


    ##
    ## BRIEF: show all instances in structure.
    ## ------------------------------------------------------------------------
    ##
    def show(self):
        return self.__instances;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
## END OF CLASS.








##############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    Instances = MCT_Instances();

## EOF.

