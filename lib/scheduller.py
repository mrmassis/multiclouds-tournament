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

<<<<<<< HEAD
        return ordenedList;
=======








class Round_Robin_Imutable_List:

    """
    Round_Robin_Imutable_List: round robin with imutable list.
    ---------------------------------------------------------------------------
    * run == execute the scheduller.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __lastPosition = 0;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):
        self.__lastPosition = 0;


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## Brief: choice the best player considered position in clock.
    ## ------------------------------------------------------------------------
    ## @PARAM list players == a list of player from a specific division.
    ##
    def run(self, players):
        selectedPlayer = players[self.__lastPosition];
        
        ## Increment to get the next element in next request:
        self.__lastPosition += 1;

        ## If the list in the end, reset the index to begin of the player list.
        if self.__lastPosition == len(players):
            self.__lastPosition = 0;

        selected = self.__return_player(selectedPlayer);

        return selected;
        

    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: format the return.
    ## ------------------------------------------------------------------------
    ## @PARAM selectedPlayer == player selected.
    ##
    def __return_player(self, selectedPlayer):
        selected = {
            'name' : selectedPlayer[1],
            'addr' : selectedPlayer[2]
        };

        return selected;

>>>>>>> 97d83ac5f11202bf8acdb187d826899f396f2beb
## EOF.
