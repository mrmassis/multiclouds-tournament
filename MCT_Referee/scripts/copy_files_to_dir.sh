#!/bin/bash








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
PATH_CODE_SRC=".."
PATH_CONF_SRC="../configuration_files/"

## If debian == dist_packages!
## If centOs == site_packages!

PATH_CODE_DST="/usr/lib/python2.7/dist-packages/mct"
PATH_CONF_DST="/etc/mct/"
PATH_LOGS_DST="/var/log/mct"

SERVICES="MCT_Dispatch.py  MCT_Divisions.py  MCT_Referee.py  MCT_Register.py MCT_Sanity.py"



###############################################################################
## FUNCTIONS                                                                 ##
###############################################################################




###############################################################################
## MAIN                                                                      ##
###############################################################################
echo "Copy MCT REFEREE FILES TO APROPRIATE FOLDERS"

mkdir -p ${PATH_CODE_DST}
mkdir -p ${PATH_CONF_DST}
mkdir -p ${PATH_LOGS_DST}

## Create __init__.py file in lib folder. This is used to enable the modules to
## used.
touch ${PATH_CODE_DST}/__init__.py

## Copy the service file to respectives place in the system.
for SERVICE in ${SERVICES}; do
    ## Copy:
    /bin/cp ${PATH_CODE_SRC}/${SERVICE} ${PATH_CODE_DST};
done

## Copy all libraries (suporte files) to destination folder.
/bin/cp -r ${PATH_CODE_SRC}/lib ${PATH_CODE_DST};

## Copy all configurtions file to destination folder in etc.
/bin/cp ${PATH_CONF_SRC}/*.ini ${PATH_CONF_DST}/

echo "DONE"
## EOF.
