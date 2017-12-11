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
## DESCRIPTION                                                              ##
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
    ## BRIEF: check if the instance exist.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def check(self, msg):

        ## If the reqId in dictionary means that the instance was created and
        ## is running. 
        for vplayer in self.__instances.keys():
            if msg['reqId'] in self.__instances[vplayer]:

                ## Check if the instance is running:
                status = self.__instances[vplayer][msg['reqId']]['status'];

                if status == 'running':
                    return True;

        return False;


    ##
    ## BRIEF: insert an instance in dicitionary.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def add(self, msg):
 
        playerSrc = msg['playerId'];
        requestId = msg['reqId'   ];

        ## Check if the instance already running:
        for player in self.__instances.keys():
            if requestId in self.__instances[player]:
                if self.__instances[player][requestId]['status'] != 'failed':
                    return False;

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

        return True;


    ##
    ## BRIEF: remove an instance from structure.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def del(self, msg):

        playerOrign = msg['playerId'];

        try:
            ## Remove from structure the instance:
            if self.__instances[playerOrign][msg['reqId']]['status'] == 'running':
                self.__instances[playerOrign].pop(msg['reqId'], None);

        except:
            pass;

        return 0;


    ##
    ## BRIEF: return flavor id from an instance.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def flavor(self, msg):

        playerOrign = msg['playerId'];

        ## Get flavor ID:
        flavorId = self.__instances[playerOrign][msg['reqId']]['flavor'];

        ## Get the index of the flavor identify:
        idx = FLV_NAME.keys()[FLV_NAME.values().index(flavorId)];

        return idx;


    ##
    ## BRIEF: update an instance in dicitionary.
    ## ------------------------------------------------------------------------
    ## @PARAM msg == message with instance data.
    ##
    def update(self, msg):

        playerOrign = msg['playerId'];
        playerGuest = msg['destName'];

        if msg['status'] == 1:
            self.__instances[playerOrign][msg['reqId']]['guest' ] = playerGuest;
            self.__instances[playerOrign][msg['reqId']]['status'] = 'running';

            ## If the request to new instance was succefull accpet so increment
            ## the totals.
            self.__increment_instances(playerGuest);
        else:
            self.__instances[playerOrign][msg['reqId']]['status'] = 'failed';

        return 0;


    ##
    ## BRIEF: show all instances in structure.
    ## ------------------------------------------------------------------------
    ##
    def show(self):
        return str(self.__instances);


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## ------------------------------------------------------------------------
    ##
    def __increment_instances(self, playerDestiny):
        return 0;

## END OF CLASS.








##############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    Instances = MCT_Instances();

## EOF.

