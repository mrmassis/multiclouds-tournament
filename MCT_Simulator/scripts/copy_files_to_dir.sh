#!/bin/bash








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
PATH_CODE_SRC=".."
PATH_CONF_SRC="../configuration_files/"

PATH_CODE_DST="/usr/lib/python2.7/dist-packages/mct/"
PATH_CONF_DST="/etc/mct/"
PATH_LOGS_DST="/var/log/mct"
PATH_VCFG_DST="/etc/mct/vplayers"
PATH_VQTA_DST="/etc/mct/quotas"

SERVICES="MCT_Agent_Simulator.py MCT_DB_Proxy.py MCT_Driver_Simulator.py"




###############################################################################
## FUNCTIONS                                                                 ##
###############################################################################




###############################################################################
## MAIN                                                                      ##
###############################################################################
echo "Copy MCT SIMULATION FILES TO APROPRIATE FOLDERS"

mdkir -p ${PATH_CODE_DST}
mdkir -p ${PATH_CONF_DST}
mdkir -p ${PATH_VCFG_DST}
mdkir -p ${PATH_VQTA_DST}

## Copy the service file to respectives place in the system.
for SERVICE in ${SERVICES}; do
    ## Copy:
    /bin/cp ${PATH_CODE_SRC}/${SERVICE} ${PATH_CODE_DST};
done

## Copy all libraries (suporte files) to destination folder.
/bin/cp ${PATH_CODE_SRC}/lib/*.py ${PATH_CODE_DST}/lib/;

## Copy all configurtions file to destination folder in etc.
/bin/cp ${PATH_CONF_SRC}/*.ini ${PATH_CONF_DST}/

echo "DONE"
## EOF.
