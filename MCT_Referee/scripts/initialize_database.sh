#!/bin/bash








###############################################################################
## DEFINITIONS                                                               ##
###############################################################################
DB_PASS="password"
DB_USER="root"
DB_BASE="mct"

DBTEMPLATE="../database_template/template.sql"





###############################################################################
## FUNCTIONS                                                                 ##
###############################################################################




###############################################################################
## MAIN                                                                      ##
###############################################################################
echo "INITIALIZING MCT DATABASE..."

## Init all tables utilized by MCT simulation components. This table is used by
## suport the simulation (virtual players) actions.
mysql -u${DB_USER} -p${DB_PASS} < ${DBTEMPLATE}

echo "DONE"
## EOF.
