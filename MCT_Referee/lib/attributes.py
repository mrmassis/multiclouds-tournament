#!/usr/bin/python








###############################################################################
## IMPORT                                                                    ##
###############################################################################
__all__ = ['MCT_Attributes'];

from mct.lib.utils import *;





###############################################################################
## DEFINITION                                                                ##
###############################################################################





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
    __pS      = 0.1;
    __pM      = 0.5;
    __pB      = 1.0;
    __cost    = 1.0;
    __flavors = {};


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self):

        self.__flavors = {
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


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: calculate the score.
    ## -----------------------------------------------------------------------
    ## @PARAM requests == list of requests.
    ## 
    def calculate_score(self, requests):
        accepts = 0;
        rejects = 0;
 
        fS = 0;
        fM = 0;
        fB = 0;

        for request in requests:
            status = int(request['status']);

            if status == SUCCESS and status == FINISHED:

                memory = request['mem'  ];
                vcpus  = request['vcpus'];
                disk   = request['disk' ];

                flavor = self.__get_flavor(memo, vcpus, disk);

                if   flavor == "S":
                    fS += 1;
                elif flavor == "M":
                    fM += 1;
                elif flavor == "B":
                    fB += 1;
            else:
                rejects += 1;

        ## Calculate the score:
        totalAccepts = (fS*self.__pS + fM*self.__pM + fB*self.__pB);
        totalRejects = (rejects*self.__cost);

        nScore = totalAccepts - totalRejects;

        return nScore;


    ##
    ## BRIEF: calculate the score.
    ## -----------------------------------------------------------------------
    ## @PARAM score           == score of players.
    ## @PARAM history         == old history.
    ## @PARAM bottonThreshold == botton division threshold.
    ## 
    def calculate_history(self, score, history, bottonThreshold):
        history = int(history);

        if float(score) >= float(bottonThreshold):
            history += 1;

        return history;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: obtain the flavor name..
    ## -----------------------------------------------------------------------
    ## @PARAM memo == qtdy of memory.
    ## @PARAM vcpu == qtdy of virtual cpus.
    ## @PARAM disk == qtdy of disk.
    ## 
    def __get_flavor(self, memo, vcpu, disk):

        memo = int(memo);
        vcpu = int(vcpu);
        disk = int(disk);

        for flavorId, data in self.__flavors.items():
            if data['memo']==memo and data['vcpu']==vcpu and data['disk']==disk:
                return flavorId; 
## END CLASS;








###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":


    mct_attributes = MCT_Attributes();
    history = mct_attributes.calculate_history(0.1, 1, 0.5);
    print history


## END.

