#!/bin/bash








###############################################################################
## DEFINITION                                                                ##
###############################################################################
BASE=$1

VPLAYERS="playerVirtual0 playerVirtual1 playerVirtual2 playerVirtual3 playerVirtual4 playerVirtual5 playerVirtual6 playerVirtual7 playerVirtual8 playerVirtual9"

VAGENT=${BASE}/'virtual_agents/mct_agent_simulation.log* '
VDRIVE=${BASE}/'virtual_agents/mct_driver_simulation.log*'

INSTANCE_PATTERN="INTANCES"

BASEINSTOTAL=${BASE}/'formated_results/total_inst_running'
BASEINSTANCE=${BASE}/'formated_results/instance_in_player'
BASEFAIRNESS=${BASE}/'formated_results/fairness_by_player'
BASEREQUESTS=${BASE}/'formated_results/requests_by_player'
BASEACCEPTED=${BASE}/'formated_results/accepted_by_player'








###############################################################################
## DEFINITION                                                                ##
###############################################################################
##
## BRIEF:
## ----------------------------------------------------------------------------
##
function instances_in_va() {

    mkdir -p ${BASEINSTANCE}
    mkdir -p ${BASEINSTOTAL}

    ## Create a temporary file that will be used to store the instace entries:
    TMPFILE=$(tempfile -s "_instance")

    for FILE in $(ls ${VAGENT} |sort -k 3,3n -t'.' |tac); do
        egrep ${INSTANCE_PATTERN} "${FILE}" >> ${TMPFILE}
    done

    ##
    cat ${TMPFILE} |while read LINE; do
        
        F1=$(echo ${LINE} |cut -d'|' -f1)
        F2=$(echo ${LINE} |cut -d'|' -f2)
        F3=$(echo ${LINE} |cut -d'|' -f3)

        ##
        DATA=$(echo ${F1} |cut -d' ' -f1)
        HORA=$(echo ${F1} |cut -d' ' -f2 |cut -d',' -f1)

        ##
        for PLAYER in ${F2}; do
         
            FILENAME="${BASEINSTANCE}/$(echo ${PLAYER} |cut -d';' -f1).dat"

            LOCAL_T=$(echo ${PLAYER} |cut -d';' -f2|cut -d':' -f2)
            LOCAL_S=$(echo ${PLAYER} |cut -d';' -f3|cut -d':' -f2)
            LOCAL_M=$(echo ${PLAYER} |cut -d';' -f4|cut -d':' -f2)

            echo "${DATA}_${HORA};${LOCAL_T};${LOCAL_S};${LOCAL_M}" >> ${FILENAME}
        done

        ##
        TOTAL_T=$(echo ${F3} |cut -d',' -f1|cut -d':' -f2)
        TOTAL_S=$(echo ${F3} |cut -d',' -f2|cut -d':' -f2)
        TOTAL_M=$(echo ${F3} |cut -d',' -f3|cut -d':' -f2)

        FILENAME="${BASEINSTOTAL}/total.dat"

        ##
        echo "${DATA}_${HORA};${TOTAL_T};${TOTAL_S};${TOTAL_M}" >> ${FILENAME}
    done

    ## Delete temporary file:
    rm ${TMPFILE}
}




##
## BRIEF: extract all lines that have the FAIRNESS tags. Divide the results by
##        virtual agents.
## ----------------------------------------------------------------------------
##
function fairness_by_vp() {

    mkdir -p ${BASEFAIRNESS}

    ## Create a temporary file that will be used to store the request entries:
    TMPFILE=$(tempfile -s "_fairness")

    ## Extract the REQUEST logs:
    for FILE in $(ls ${VDRIVE} |sort -k 3,3n -t'.' |tac); do
        egrep "FAIRNESS:" "${FILE}" >> ${TMPFILE}
    done

    ### Divide found entries in separeted files (by individual virtual player):
    for VPLAYER in ${VPLAYERS}; do

        ## Create temporary file:
        TMPFILE2=$(tempfile -s "_fairness_${VPLAYER}")

        egrep "${VPLAYER}" "${TMPFILE}" >> "${TMPFILE2}"

        FILENAME="${BASEFAIRNESS}/${VPLAYER}_fairness.dat"

        ## Extract the apropriate fields:
        cat ${TMPFILE2} |while read LINE; do
            ##
            DATA=$(echo ${LINE} |cut -d' ' -f1)
            HORA=$(echo ${LINE} |cut -d' ' -f2 |cut -d',' -f1)

            FAIRNESS=$(echo ${LINE} |cut -d'|' -f2)
      
            echo "${DATA}_${HORA};${FAIRNESS}" >> ${FILENAME}
        done

        ## Delete temporary file:
        rm ${TMPFILE2}
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

    mkdir -p ${BASEREQUESTS}

    ## Create a temporary file that will be used to store the request entries:
    TMPFILE=$(tempfile -s "_requests")

    ## Extract the REQUEST logs:
    for FILE in $(ls ${VDRIVE} |sort -k 3,3n -t'.' |tac); do
        egrep "REQUESTS:" "${FILE}" >> ${TMPFILE}
    done

    ## Divide found entries in separeted files (by individual virtual player):
    for VPLAYER in ${VPLAYERS}; do

        ## Create temporary file:
        TMPFILE2=$(tempfile -s "_requests_${VPLAYER}")

        egrep "${VPLAYER}" "${TMPFILE}" >> "${TMPFILE2}"

        FILENAME="${BASEREQUESTS}/${VPLAYER}_requests.dat"

        ## Extract the apropriate fields:
        cat ${TMPFILE2} |while read LINE; do
            ##
            DATA=$(echo ${LINE} |cut -d' ' -f1)
            HORA=$(echo ${LINE} |cut -d' ' -f2 |cut -d',' -f1)

            REQUESTS=$(echo ${LINE} |cut -d'|' -f2)

            echo "${DATA}_${HORA};${REQUESTS}" >> ${FILENAME}
        done

        ## Delete temporary file:
        rm ${TMPFILE2}
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

    mkdir -p ${BASEACCEPTED}

    ## Create a temporary file that will be used to store the request entries:
    TMPFILE=$(tempfile -s "_accepted")

    ## Extract the ACCEPTED logs:
    for FILE in $(ls ${VDRIVE} |sort -k 3,3n -t'.' |tac); do
        egrep "ACCEPTED:" "${FILE}" >> ${TMPFILE}
    done

    ## Divide found entries in separeted files (by individual virtual player):
    for VPLAYER in ${VPLAYERS}; do

        ## Create temporary file:
        TMPFILE2=$(tempfile -s "_accepted_${VPLAYER}")

        egrep "${VPLAYER}" "${TMPFILE}" >> "${TMPFILE2}"

        FILENAME="${BASEACCEPTED}/${VPLAYER}_accepted.dat"

        ## Extract the apropriate fields:
        cat ${TMPFILE2} |while read LINE; do
            ##
            DATA=$(echo ${LINE} |cut -d' ' -f1)
            HORA=$(echo ${LINE} |cut -d' ' -f2 |cut -d',' -f1)

            ACCEPTED=$(echo ${LINE} |cut -d'|' -f2)

            echo "${DATA}_${HORA};${ACCEPTED}" >> ${FILENAME}
        done

        ## Delete temporary file:
        rm ${TMPFILE2}
    done

    ## Delete temporary file:
    rm ${TMPFILE}
}








###############################################################################
## MAIN                                                                      ##
###############################################################################
instances_in_va;

fairness_by_vp
requests_by_vp
accepted_by_vp


## EOF.
