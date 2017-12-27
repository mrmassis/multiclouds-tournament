#!/bin/bash








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
PATH_LOG_SRC="/var/log/mct"
PATH_LOG_DST="/var/log/mct/$(date +%D_%T |tr '/' '-')"

LOGS="mct_dispatch.log mct_divisions.log mct_referee.log mct_register.log mct_sanity.log"



###############################################################################
## FUNCTIONS                                                                 ##
###############################################################################




###############################################################################
## MAIN                                                                      ##
###############################################################################
echo "COPY MCT REFEREE LOGS TO APROPRIATE FOLDER"

## Create a specific folder (with timestamp) to copy the execution test logs.
mkdir -p ${PATH_LOG_DST}

## Copy the service file to respectives place in the system.
for LOG in ${LOGS}; do
    ## Copy:
    /bin/cp ${PATH_LOG_SRC}/${LOG}* ${PATH_LOG_DST};
done

## Delete the olders logs.
rm -f ${PATH_LOG_SRC}/* 2> /dev/null

echo "DONE"
## EOF.
