#!/bin/bash


###############################################################################
## DEFINITION                                                                ##
###############################################################################
AZ_NAME="multicloud-tournament"
HT_NAME="agent-1"



###############################################################################
## RABBITMQ                                                                  ##
###############################################################################
rabbitmqctl add_user mct password
rabbitmqctl set_permissions mct ".*" ".*" ".*"




###############################################################################
## CREATE AGGREGATION ZONE                                                   ##
###############################################################################
EXIST=$(nova aggregate-list|grep ${AZ_NAME})

if [ -z ${EXIST} ]; then
    nova aggregate-create ${AZ_NAME} ${AZ_NAME}
    ID=$(nova aggregate-list|grep ${AZ_NAME} | cut -d'|' -f2)
    nova aggregate-add-host 1 ${HT_NAME}
fi

## EOF.
