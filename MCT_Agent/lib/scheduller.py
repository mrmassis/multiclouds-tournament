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
    ##
    def run(self, players):
        selected = {};
       
        ## Sort the received playerList by player' score: 
        tempList = sorted(players, key=lambda field: field[4], reverse=True);

        if len(tempList) > 0:

            ## Select player from the main list. Remove the first list element.
            returnedPosition = tempList.pop(0);

            selected = { 
                'name' : returnedPosition[1],
                'addr' : returnedPosition[2] 
            }

        return selected;

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
        selected = {};
       
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
            returnedPosition = self.__clocker.pop(0);

            ## Insert the returned position to final list position (__clocker).
            self.__clocker.append(returnedPosition);

            selected = {
                'name' : returnedPosition[1],
                'addr' : returnedPosition[2] 
            };

        ## Return the selected player. 
        return selected;

## EOF.
