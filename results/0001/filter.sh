#!/bin/bash








###############################################################################
## DEFINITION                                                                ##
###############################################################################
VPLAYERS="playerVirtual0 playerVirtual1 playerVirtual2 playerVirtual3 playerVirtual4 playerVirtual5 playerVirtual6 playerVirtual7 playerVirtual8 playerVirtual9"

VAGENT='virtual_agents/mct_agent_simulation.log*'
VDRIVE='virtual_agents/mct_drive_simulation.log*'





###############################################################################
## DEFINITION                                                                ##
###############################################################################
##
## BRIEF:
## ----------------------------------------------------------------------------
##
function instances_in_va() {

    ## Create a temporary file that will be used to store the instace entries:
    #TMPFILE=$(tempfile -s "_instance")

    #for FILE in $(ls ${VAGENT} |sort -k 3,3n -t'.' |tac); do
    #    egrep "INSTANCES:" "${FILE}" >> ${TMPFILE}
    #done

    TMPFILE="teste.txt"
    
    TOTAL="total.txt"

    ##
    cat ${TMPFILE} |while read LINE; do
        
        F1=$(echo ${LINE} |cut -d'|' -f1)
        F2=$(echo ${LINE} |cut -d'|' -f2)
        F3=$(echo ${LINE} |cut -d'|' -f3)

        ##
        DATA=$(echo ${F1} |cut -d' ' -f1)
        HORA=$(echo ${F1} |cut -d' ' -f2)

        ##
        for PLAYER in ${F2}; do
         
            NAME="$(echo ${PLAYER} |cut -d';' -f1).txt"

            LOCAL_T=$(echo ${PLAYER} |cut -d';' -f2|cut -d':' -f2)
            LOCAL_S=$(echo ${PLAYER} |cut -d';' -f3|cut -d':' -f2)
            LOCAL_M=$(echo ${PLAYER} |cut -d';' -f4|cut -d':' -f2)

            echo "${DATA};${HORA};${LOCAL_T};${LOCAL_S};${LOCAL_M}" >> ${NAME}
        done

        ##
        TOTAL_T=$(echo ${F3} |cut -d';' -f1|cut -d':' -f2)
        TOTAL_S=$(echo ${F3} |cut -d';' -f2|cut -d':' -f2)
        TOTAL_M=$(echo ${F3} |cut -d';' -f3|cut -d':' -f2)

        ##
        echo "${DATA};${HORA};${TOTAL_T};${TOTAL_S};${TOTAL_M}" >> ${TOTAL}
    done

    ## Delete temporary file:
    #rm ${TMPFILE}
}




##
## BRIEF: extract all lines that have the FAIRNESS tags. Divide the results by
##        virtual agents.
## ----------------------------------------------------------------------------
##
function fairness_by_vp() {

    ## Create a temporary file that will be used to store the request entries:
    TMPFILE=$(tempfile -s "_fairness")

    ## Extract the REQUEST logs:
    for FILE in $(ls ${VDRIVE} |sort -k 3,3n -t'.' |tac); do
        egrep "FAIRNESS:" "${FILE}" >> ${TMPFILE}
    done

    ## Divide found entries in separeted files (by individual virtual player):
    for VPLAYER in ${VPLAYERS}; do
        FILENAME="formated_results/${VPLAYER}_fairness_va.txt"

        egrep "${VPLAYER}" "${TMPFILE}" > "${FILENAME}"
    done

    ## Delete temporary file:
    rm ${TMPFILE}
}




##
## BRIEF: extract all lines that have the REQUESTS tags. Divide the results by
##        virtual agents.
## ----------------------------------------------------------------------------
##
function requests_by_vp() {

    ## Create a temporary file that will be used to store the request entries:
    TMPFILE=$(tempfile -s "_requests")

    ## Extract the REQUEST logs:
    for FILE in $(ls ${VDRIVE} |sort -k 3,3n -t'.' |tac); do
        egrep "REQUESTS:" "${FILE}" >> ${TMPFILE}
    done

    ## Divide found entries in separeted files (by individual virtual player):
    for VPLAYER in ${VPLAYERS}; do
        FILENAME="formated_results/${VPLAYER}_requests_va.txt"

        egrep "${VPLAYER}" "${TMPFILE}" > "${FILENAME}"
    done

    ## Delete temporary file:
    rm ${TMPFILE}
}




##
## BRIEF: extract all lines that have the ACCEPTED tags. Divide the results by
##        virtual agents.
## ----------------------------------------------------------------------------
##
function accepted_by_vp() {

    ## Create a temporary file that will be used to store the request entries:
    TMPFILE=$(tempfile -s "_accepted")

    ## Extract the REQUEST logs:
    for FILE in $(ls ${VDRIVE} |sort -k 3,3n -t'.' |tac); do
        egrep "ACCEPTED:" "${FILE}" >> ${TMPFILE}
    done

    ## Divide found entries in separeted files (by individual virtual player):
    for VPLAYER in ${VPLAYERS}; do
        FILENAME="formated_results/${VPLAYER}_accepted_va.txt"

        egrep "${VPLAYER}" "${TMPFILE}" > "${FILENAME}"
    done

    ## Delete temporary file:
    rm ${TMPFILE}
}








###############################################################################
## MAIN                                                                      ##
###############################################################################
instances_in_va;


## EOF.
