#!/bin/bash



## ------------------------------------------------------------------------- ##
## Definition.                                                               ##   
## ------------------------------------------------------------------------- ##


echo "Initializing the MCT databes..."

## ------------------------------------------------------------------------- ##
## Init all tables utilized by MCT components.                               ##
## ------------------------------------------------------------------------- ##
mysql -uroot -ppassword mct < templates.sql


## ------------------------------------------------------------------------- ##
## Load machine data to SIMULATION table in MCT database.                    ##
## ------------------------------------------------------------------------- ##
mysql -uroot -ppassword mct < simulation_table_machine_data.sql
echo "Done"

## EOF.
