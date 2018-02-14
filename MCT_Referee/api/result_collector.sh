#!/bin/bash



###############################################################################
## DEFINITION                                                                ##
###############################################################################
DBBASE="mct"
DBUSER="mct"
DBPASS="password"
CMYSQL="mysql -N -u${DBUSER} -p${DBPASS} ${DBBASE}"
INSTVM_FILE="instance.dat"
STATUS_FILE="sgf.dat"

PLAYER0="playerVirtual0"
PLAYER1="playerVirtual1"
PLAYER2="playerVirtual2"
PLAYER3="playerVirtual3"
PLAYER4="playerVirtual4"
PLAYER5="playerVirtual5"
PLAYER6="playerVirtual6"
PLAYER7="playerVirtual7"
PLAYER8="playerVirtual8"
PLAYER9="playerVirtual9"

DIVISION1_FILE="division1.dat"
DIVISION2_FILE="division2.dat"
DIVISION3_FILE="division3.dat"
ELIMINATD_FILE="eliminated.dat"

DIVS_FILE="divisions.dat"
MYSQL_DUMP="mysqlmct_dump.sql"




###############################################################################
## HEADER                                                                    ##
###############################################################################
echo "SAMPLE RUNNING CHEATING FINISHED"     > ${INSTVM_FILE}
echo "PLAYERS REQUESTS FAIRNESS FREERIDERS" > ${STATUS_FILE}

echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER0}.dat
echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER1}.dat
echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER2}.dat
echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER3}.dat
echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER4}.dat
echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER5}.dat
echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER6}.dat
echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER7}.dat
echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER8}.dat
echo "NAME HISTORY FAIRNESS MAX_INSTANCE FREERIDERS" > ${PLAYER9}.dat

echo "NAME SCORE HISTORY FAIRNESS ENABLE PLAYOFF" > ${DIVISION1_FILE}
echo "NAME SCORE HISTORY FAIRNESS ENABLE PLAYOFF" > ${DIVISION2_FILE}
echo "NAME SCORE HISTORY FAIRNESS ENABLE PLAYOFF" > ${DIVISION3_FILE}
echo "NAME SCORE HISTORY FAIRNESS ENABLE PLAYOFF" > ${ELIMINATD_FILE}

echo "DIVISION PLAYERS" > ${DIVS_FILE}





###############################################################################
## MAIN                                                                      ##
###############################################################################
COUNT=0
while true; do

    ## -----
    ## INSTANCES
    ## -----
    ## Execute the command: 
    R=$(${CMYSQL} -e "select * from VM where status=1" |wc -l)
    C=$(${CMYSQL} -e "select * from VM where status=2" |wc -l)
    F=$(${CMYSQL} -e "select * from VM where status=3" |wc -l)
    echo ${COUNT} ${R} ${C} ${F} >> ${INSTVM_FILE}


    ## -----
    ## INDIVIDUAL FAIRNESS VERSUS FREERIDERS
    ## -----
    FIELD="name,history,fairness,max_instance"
    TMPFILE=$(mktemp)
    ${CMYSQL} -e "select ${FIELD} from PLAYER" |while read RECORD; do
        echo ${RECORD} >> ${TMPFILE}
    done

    FREERIDERS=$(egrep 'playerVirtual[0-9]{2}' ${TMPFILE} |wc -l)


    echo "$(grep "${PLAYER0} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER0}.dat
    echo "$(grep "${PLAYER1} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER1}.dat
    echo "$(grep "${PLAYER2} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER2}.dat
    echo "$(grep "${PLAYER3} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER3}.dat
    echo "$(grep "${PLAYER4} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER4}.dat
    echo "$(grep "${PLAYER5} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER5}.dat
    echo "$(grep "${PLAYER6} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER6}.dat
    echo "$(grep "${PLAYER7} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER7}.dat
    echo "$(grep "${PLAYER8} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER8}.dat
    echo "$(grep "${PLAYER9} " ${TMPFILE}) ${FREERIDERS}" >> ${PLAYER9}.dat
    rm -f ${TMPFILE}


    if [[ "${COUNT}" == ${1} ]]; then
        ## ---
        ## GLOBAL FAIRNESS VERSUS FREERIDERS
        ## ---
        FIELDS="players,all_requests,fairness"
        ${CMYSQL} -e "select ${FIELDS} from STATUS" |while read LINE; do
            LINE=$(echo ${LINE} |tr -s ' ')
            echo "${LINE} ${FREERIDERS}" >> ${STATUS_FILE}
        done 

        ## ---
        ## DIVISIONS
        ## ---
        FIELDS="name,division,score,history,fairness,enabled,playoff"
        ${CMYSQL} -e "select ${FIELDS} from PLAYER"|while read LINE; do
            DIVISION=$(echo ${LINE}|cut -d' ' -f2)

            case "${DIVISION}" in
                "1") echo ${LINE} >> ${DIVISION1_FILE}
                     ;;
                "2") echo ${LINE} >> ${DIVISION2_FILE}
                     ;;
                "3") echo ${LINE} >> ${DIVISION3_FILE}
                     ;;
                *)   echo ${LINE} >> ${ELIMINATD_FILE}
                     ;;
            esac
        done

        echo "1 $(cat ${DIVISION1_FILE} |tail -n+2 |wc -l)" >> ${DIVS_FILE}
        echo "2 $(cat ${DIVISION2_FILE} |tail -n+2 |wc -l)" >> ${DIVS_FILE}
        echo "3 $(cat ${DIVISION3_FILE} |tail -n+2 |wc -l)" >> ${DIVS_FILE}
        echo "4 $(cat ${ELIMINATD_FILE} |tail -n+2 |wc -l)" >> ${DIVS_FILE}

        ## MYSQLDUMP
        mysqldump -u${DBUSER} -p${DBPASS} ${DBBASE} > ${MYSQL_DUMP}

        echo "EXIT"
        exit

    fi

    COUNT=$((COUNT + 1))
    sleep 300
    echo $COUNT
done

## EOF.
