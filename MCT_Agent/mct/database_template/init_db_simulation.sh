#!/bin/bash



## ------------------------------------------------------------------------- ##
## Definition.                                                               ##   
## ------------------------------------------------------------------------- ##


echo "Initializing the MCT database..."

## ------------------------------------------------------------------------- ##
## Init all tables utilized by MCT components.                               ##
## ------------------------------------------------------------------------- ##
mysql -uroot -ppassword mct < /etc/mct/database_template/templates.sql
echo "Done"

## EOF.
