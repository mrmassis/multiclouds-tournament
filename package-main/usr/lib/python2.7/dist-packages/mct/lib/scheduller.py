#!/usr/bin/env python


import sys;
import os;


###############################################################################
## DEFINITIONS                                                               ##
###############################################################################




###############################################################################
## CLASSES                                                                   ##
###############################################################################
class Bestscores:

    """
    Class Bestscores.
    ---------------------------------------------------------------------------
    * run == execute the scheduller.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __restricts = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, restrict = ''):
        self.__restrict = restrict;


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## Brief: choice the best player considered bestscores.
    ## ------------------------------------------------------------------------
    ## @PARAM list playerList     == a list of player from a specific division.
    ## @PARAM str  playerResquest == id from player who made the request.
    ##
    def run(self, playerList):
        
        tempList = sorted(playerList, key=lambda field: field[4], reverse=True);

        ordenedList = [];
        for player in tempList:
            dictPlayer = {
                'name' : player[1],
                'addr' : player[2] 
            }

            ordenedList.append(dictPlayer);

        return ordenedList;
## EOF.
