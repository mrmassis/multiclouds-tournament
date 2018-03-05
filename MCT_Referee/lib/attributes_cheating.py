#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
__all__ = ['MCT_Attributes'];

from mct.lib.utils import *;





###############################################################################
## DEFINITION                                                                ##
###############################################################################
L_COST =  1.0

WEIGHT_S = 1.33;
WEIGHT_M = 1.66;
WEIGHT_B = 1.99;

FLAVORS = {
    "S" : {
          'memo' : 512,
          'vcpu' : 1,
          'disk' : 1
     },
     "M" : {
          'memo' : 2048,
          'vcpu' : 1,
          'disk' : 20
     },
     "B" : {
          'memo' : 4096,
          'vcpu' : 2,
          'disk' : 40
     }
};




###############################################################################
## CLASSES                                                                   ##
###############################################################################
class MCT_Attributes(object):

    """
    MCT_Attributes perform the attribute calculate.
    ---------------------------------------------------------------------------
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
    ## BRIEF: calculate the score.
    ## -----------------------------------------------------------------------
    ## @PARAM requests == list of requests.
    ## 
    @staticmethod
    def calculate_score(self, requests):
        totalAccepts = 0;
        totalRejects = 0;
 
        fS = 0;
        fM = 0;
        fB = 0;

        for request in requests:
            status = int(request['status']);

            if status == SUCCESS or status == FINISHED:

                m = request['mem'  ];
                v = request['vcpus'];
                d  = request['disk' ];

               for flavorId, data in FLAVORS.items():
                     if data['memo']==m and data['vcpu']==c and data['disk']==d:
                         break;

                if   flavorId == "S":
                    fS += 1;
                elif flavorId == "M":
                    fM += 0;
                elif flavorId == "B":
                    fB += 1;
            else:
                TotalRejects += 1 * L_COST;

        ## Calculate the score:
        totalAccepts = (fS * WEIGHT_S) + (fM * WEIGHT_M) + (fB * WEIGHT_B);

        nScore = totalAccepts - totalRejects;
        return nScore;


    ##
    ## BRIEF: calculate the score.
    ## -----------------------------------------------------------------------
    ## @PARAM score           == score of players.
    ## @PARAM history         == old history.
    ## @PARAM bottonThreshold == botton division threshold.
    ## 
    @staticmethod
    def calculate_history(self, score, history, bottonThreshold):
        history = int(history);

        if float(score) >= float(bottonThreshold):
            history += 1;

        return history;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
## END CLASS;








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    mct_attributes = MCT_Attributes();
    history = mct_attributes.calculate_history(0.1, 1, 0.5);
    print history

## END.

