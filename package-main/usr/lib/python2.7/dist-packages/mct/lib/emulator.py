#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
__all__ = ['MCT_Emulator'];







###############################################################################
## DEFINITION                                                                ##
###############################################################################








###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Emulator(object):

    """
    Class that emulate the player action.
    ---------------------------------------------------------------------------
    create_instance == create a new instance.
    delete_instance == delete an existent instante.
    """

    ###########################################################################
    ## DEFINITION                                                           ##
    ###########################################################################


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: emule the instance creation.
    ## -----------------------------------------------------------------------
    ## @PARAM instanceL == instance label.
    ## @PARAM imageL    == image label.
    ## @PARAM flavorL   == flavor label.
    ## @PARAP networkL  == network label.
    ## 
    def create_instance(self, intanceL, imageL, flavorL, networkL):
        ## RETURN ONE FROM A SET THE EVENT.
        creationStates = ['NOSTATE', 'ERROR', 'ACTIVE'];
        return creationStates[1];


    ##
    ## BRIEF: emule the deletion of the instance.
    ## -----------------------------------------------------------------------
    ## @PARAM uuid == instance uuid.
    ## 
    def delete_instance(self, uuid):
        return 'HARD_DELETED';  


## END.

