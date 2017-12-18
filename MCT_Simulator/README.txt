## Create rabbitmq user and set permission 
rabbitmqctl add_user mct password
rabbitmqctl set_permissions mct ".*" ".*" ".*"


## Folders
simulations........: simulations test map
configuration_files: services configurate files.
database_template..: templates to sql schema and simulation database.
scripts............: auxiliary scripts (initialize the database, copy files ...).
vplayer_template...: virtual player template.
