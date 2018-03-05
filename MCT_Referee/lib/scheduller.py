#!/usr/bin/env python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
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
    ##
    def run(self, players):
        selectedPlayer = {};
       
        ## Sort the received playerList by player' score: 
        tempList = sorted(players, key=lambda field: field[4], reverse=True);

        if len(tempList) > 0:

            ## Select player from the main list. Remove the first list element.
            selectedPlayer = tempList.pop(0);

        return selectedPlayer;

## END CLASS.







class Clock:

    """
    Class Clock: give a player in clock mode.
    ---------------------------------------------------------------------------
    * run == execute the scheduller.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __clocker = [];


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## Brief: choice the best player considered position in clock.
    ## ------------------------------------------------------------------------
    ## @PARAM list players == a list of player from a specific division.
    ##
    def run(self, players):
        selectedPlayer = {};
       
        ## Create two main lists - the remove list: elements that will be remo-
        ## ved from original list (__clocker). The insert list has all elements
        ## that will be inserted to original list (__clocker).
        remove = [x for x in self.__clocker if x not in self.__players];
        insert = [x for x in self.__players if x not in self.__clocker];

        ## Remove the elements that not exist in the received list.Now the list
        ## has the only valids elements (update list).
        self.__clocker = [x for x in self.__clocker if x not in remove];

        ## Insert the news elements presents in the received list in the actual
        ## list (__clocker).
        self.__clocker = self.__clocker + insert;

        ## Check if the list is empty:
        if len(self.__clocker) > 0:

            ## Select player from the main list. Remove the first list element.
            selectedPlayer = self.__clocker.pop(0);

            ## Insert the returned position to final list position (__clocker).
            self.__clocker.append(selectedPlayer);

        ## Return the selected player. 
        return selectedPlayer;









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

        return selectedPlayer;
        

    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
## END CLASS.








class Timestamp:

    """
    Timestamp:
    ---------------------------------------------------------------------------
    * run == execute the scheduller.
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## Brief: choice the best player considered the last player choiced.
    ## ------------------------------------------------------------------------
    ## @PARAM list players == a list of player from a specific division.
    ##
    def run(self, players):
        playersSorted = sorted(players, key=lambda k: k['last_choice']);

        for player in playersSorted:
            
            ## Minimize reject requests:
            if (int(player['running']) + 1) <= int(player['max_instance']):
                player['hasResources'] = 1;
                return player;

        ## In this case the probability of reject request is 99.99999.
        player = playersSorted[0];

        ## Set to mitigate coalition effects:
        player['hasResources'] = 0;

        return player;



    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################


## EOF.
