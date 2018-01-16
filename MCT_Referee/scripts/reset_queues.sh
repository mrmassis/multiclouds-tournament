#!/bin/bash








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################



###############################################################################
## FUNCTIONS                                                                 ##
###############################################################################




###############################################################################
## MAIN                                                                      ##
###############################################################################
echo "RESET ALL QUEUES"

rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl start_app

rabbitmqctl add_user mct password
rabbitmqctl set_permissions mct ".*" ".*" ".*"

echo "DONE"
## EOF.
