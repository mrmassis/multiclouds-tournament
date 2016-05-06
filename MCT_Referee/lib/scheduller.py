#!/usr/bin/env python


import sys;
import os;


###############################################################################
## DEFINITIONS                                                               ##
###############################################################################




###############################################################################
## CLASSES                                                                   ##
###############################################################################
class Roundrobin:

    """
    Classe que um metodos de scheduller -- Round Robin.
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
    ## Brief: choice the best player.
    ## ------------------------------------------------------------------------
    ## @PARAM list playerList ==
    ##
    def run(self, playerList, playerRequest):
        print playerList;

        ## TODO: o endereco do player escolhido nao pode ser o do requisitante.

        #print "Executing the Round Robin schduller...";
        #player = { 'name' : 'america',
        #           'addr' : 'locahost',
        #           'token': 'dsfskdgjdsgsdjgslkjslk'
        #          };

        #self.playersOrdenedList = [player, player, player];
        return "20.0.0.30";

## EOF.
