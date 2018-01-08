#!/bin/bash








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
PATH_QUOTAS_DST="/etc/mct/quotas"
PATH_PLAYER_DST="/etc/mct/vplayers"



###############################################################################
## FUNCTIONS                                                                 ##
###############################################################################




###############################################################################
## MAIN                                                                      ##
###############################################################################
echo "COPY MCT SIMULATION LOGS TO APROPRIATE FOLDER"

rm -f ${PATH_QUOTAS_DST}/*
rm -f ${PATH_PLAYER_DST}/*

## Copy the service file to respectives place in the system.
for ((i=0; i <= ${1}; i++)); do

    RESOURCES=""
    RESOURCES=${RESOURCES}"name         : vPlayer${i}\n"
    RESOURCES=${RESOURCES}"vcpus        : 1023\n"
    RESOURCES=${RESOURCES}"memory       : 1047552\n"
    RESOURCES=${RESOURCES}"local_gb     : 10230\n"
    RESOURCES=${RESOURCES}"max_instance : 50\n"
    RESOURCES=${RESOURCES}"strategy     : 0\n"

    echo -e ${RESOURCES} > ${PATH_QUOTAS_DST}/resources${i}.yml

    VPLAYER=""
    VPLAYER=${VPLAYER}"name                        : playerVirtual${i}\n"
    VPLAYER=${VPLAYER}"amqp_identifier             : playerVirtual${i}\n"
    VPLAYER=${VPLAYER}"amqp_address                : localhost\n"
    VPLAYER=${VPLAYER}"amqp_route                  : mct_agent\n"
    VPLAYER=${VPLAYER}"amqp_exchange               : mct_exchange\n"
    VPLAYER=${VPLAYER}"amqp_queue_name             : agent\n"
    VPLAYER=${VPLAYER}"amqp_user                   : mct\n"
    VPLAYER=${VPLAYER}"amqp_pass                   : password\n"
    VPLAYER=${VPLAYER}"agent_id                    : agent_drive_${i}\n"
    VPLAYER=${VPLAYER}"ratio                       : 610\n"
    VPLAYER=${VPLAYER}"request_pending_iteract     : 10\n"
    VPLAYER=${VPLAYER}"request_pending_waiting     : 60\n"
    VPLAYER=${VPLAYER}"authenticate_address        : 192.168.0.201\n"
    VPLAYER=${VPLAYER}"authenticate_port           : 2000\n"
    VPLAYER=${VPLAYER}"agent_address               : 192.168.0.200\n"
    VPLAYER=${VPLAYER}"resources_file              : /etc/mct/quotas/resources${i}.yml\n"
    VPLAYER=${VPLAYER}"port                        : 10000\n"
    VPLAYER=${VPLAYER}"addr                        : localhost\n"
    VPLAYER=${VPLAYER}"get_set_resources_info_time : 120\n"
    VPLAYER=${VPLAYER}"print                       : logger\n"
    VPLAYER=${VPLAYER}"enable                      : 1\n"

    echo -e ${VPLAYER}   > ${PATH_PLAYER_DST}/vplayer${i}.yml

done


echo "DONE"
## EOF.
