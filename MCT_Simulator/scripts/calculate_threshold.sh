#!/bin/bash








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
MYSQL="mysql -N -uroot -ppassword mct -e"
MAX_VALUE=9999999999999999999999999999999999
T_OLD=${MAX_VALUE}
T_NEW=${MAX_VALUE}





###############################################################################
## MAIN                                                                      ##
###############################################################################
${MYSQL} "select * from SIMULATION where eventType=0;" |while read RECORD; do

    T_NEW=${MAX_VALUE}
     
    ID_INI=$(echo ${RECORD} |cut -d' ' -f1)
    TS_INI=$(echo ${RECORD} |cut -d' ' -f2)
    VM_INI=$(echo ${RECORD} |cut -d' ' -f3)

    ## Create the query to find the delete the correspondence query.
    QUERY="select id,time from SIMULATION"
    WHERE="where eventType=1 and machineId=${VM_INI} group by machineId;"

    ## Execute query: 
    VALRET=$(${MYSQL} "${QUERY} ${WHERE}")

    ID_END=$(echo ${VALRET} |tr -s ' ' |cut -d' ' -f1)
    TS_END=$(echo ${VALRET} |tr -s ' ' |cut -d' ' -f2)

    ${MYSQL} "delete from SIMULATION where id=${ID_INI};"

    ## If the machine has finish delete the record. Otherwise do not anything.
    if [[ ! -z ${TS_END} ]]; then
        if [[ $ID_END -ge $ID_INI ]]; then
            ${MYSQL} "delete from SIMULATION where id=${ID_END};"
            T_NEW=$((TS_END - TS_INI))
        else
            continue;
        fi
    else
        continue
    fi

    ## Calcule the value:
    if [[ ${T_NEW} -lt ${T_OLD} ]]; then
        T_OLD=${T_NEW}
    fi

    ## Show the mininum value.
    ## #######################
    echo ${T_OLD} "-" ${TS_INI} "-" ${TS_END}
done

## EOF.

