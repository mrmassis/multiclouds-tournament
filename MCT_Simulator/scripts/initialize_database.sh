#!/bin/bash








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
DB_PASS="password"
DB_USER="root"
DB_BASE="mct"

DBTEMPLATE="../database_template/templates.sql"
SIMULATION="../database_template/simulation_table_machine_data.sql"





###############################################################################
## FUNCTIONS                                                                 ##
###############################################################################




###############################################################################
## MAIN                                                                      ##
###############################################################################
echo "INITIALIZING MCT DATABASE..."

## Init all tables utilized by MCT simulation components. This table is used by
## suport the simulation (virtual players) actions.
mysql -u${DB_USER} -p${DB_PASS} ${DB_BASE} < ${DBTEMPLATE}

## Load machine data to SIMULATION table in MCT database. This records are used
## to generate actions in enviroment.
mysql -uroot -ppassword mct < ${SIMULATION}

echo "DONE"
## EOF.
