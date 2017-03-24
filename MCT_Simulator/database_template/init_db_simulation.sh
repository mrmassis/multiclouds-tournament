#!/bin/bash



## ------------------------------------------------------------------------- ##
## Definition.                                                               ##   
## ------------------------------------------------------------------------- ##


echo "Initializing the MCT database..."

## ------------------------------------------------------------------------- ##
## Init all tables utilized by MCT components.                               ##
## ------------------------------------------------------------------------- ##
mysql -uroot -ppassword mct < /etc/mct/database/templates.sql


## ------------------------------------------------------------------------- ##
## Load machine data to SIMULATION table in MCT database.                    ##
## ------------------------------------------------------------------------- ##
mysql -uroot -ppassword mct < /etc/mct/database/simulation_table_machine_data.sql
echo "Done"

## EOF.
