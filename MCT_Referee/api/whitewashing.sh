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
WHITEWASHING_FILE="whitewashing.dat"
VMS_FILE="vms.dat"
MYSQL_DUMP="mysqlmct_dump.sql"




###############################################################################
## HEADER                                                                    ##
###############################################################################
echo "SAMPLE RUNNING CHEATING FINISHED"                         > ${INSTVM_FILE}
echo "PLAYER DIVISION SCORE FAIRNESS ACCEPTS REJECT"            > ${WHITEWASHING_FILE}
echo "ORIGIN STATUS TIMESTAMP_RECEIVED TIMESTAMP_FINISHED"      > ${VMS_FILE}
echo "ID PLAYER ALL_REQUEST ACCEPTS REJECTS FAIRNESS TIMESTAMP" > ${STATUS_FILE}



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

    ## !!!
    FIELDS="name,division,score,fairness,accepts,rejects"
    ${CMYSQL} -e "select ${FIELDS} from PLAYER"|while read LINE;do
        echo ${LINE} >> ${WHITEWASHING_FILE}
    done
    echo "-------" >> ${WHITEWASHING_FILE}

    if [[ "${COUNT}" == ${1} ]]; then
       FIELDS="*"
       ${CMYSQL} -e "select ${FIELDS} from VM"|while read LINE; do
           echo ${LINE} >> ${VMS_FILE}
       done

       ${CMYSQL} -e "select * from STATUS" >> ${STATUS_FILE}

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

