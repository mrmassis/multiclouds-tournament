#!/bin/bash








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
CREDS="amqp://mct:password@referee/%2f"
CMIME="application/json"
ROUTE="dispatch"
EXCHG="mct_exchange"

CODE="666"
ADDR="10.3.77.162"
ID="MCT_Simulation"



###############################################################################
## FUNCTIONS                                                                 ##
###############################################################################




###############################################################################
## MAIN                                                                      ##
###############################################################################
echo "SEND MESSAGE TO RESET THE ENVIROMENT"

MSG="{
    'code'    : ${CODE},
    'playerId': ${ID},
    'status'  : 0,
    'reqId'   : 0,
    'retId'   : '',
    'origAddr': ${ADDR},
    'destAddr': '',
    'destName': '',
    'data'    : {}
}"

## Parameters:
## -u == 
## -r == the routing key to publish with;
## -e == the name of the exchange to publish to.
## -p == use the persistent delivery mode.
## -C == specifies the content-encoding property for the message.
## -b == message to send.
##
## TODO: testar.
amqp-publish -u ${CREDS} -r "${ROUTE}" -e "${EXCHG}" -p -C ${CMIME} -b "${MSG}"

echo "DONE"
## EOF.
