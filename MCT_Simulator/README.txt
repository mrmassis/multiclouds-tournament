## Create rabbitmq user and set permission 
rabbitmqctl add_user mct password
rabbitmqctl set_permissions mct ".*" ".*" ".*"
