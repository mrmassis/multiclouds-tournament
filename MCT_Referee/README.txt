-------------------------------------------------------------------------------
-- Components:                                                               --
-------------------------------------------------------------------------------
** MCT_Dispatch.py  == dispatch correct actions.
** MCT_Divisions.py == implement the divisions in the competition.
** MCT_Referee.py   == competition referee.
** MCT_Registry.py  == registry players to competition.
** MCT_Sanity.py    == check if the VMs are running in remote players.
--

-------------------------------------------------------------------------------
-- Dependences in CentOS                                                     --
-------------------------------------------------------------------------------
-- yum install epel-release 
* python2-pika i
* rabbitmq-server 
* python2-yamlordereddictloader 
* MySQL-python 
* mysql-connector-python
* python-sqlalchemy
* mariadb-server

-- systemctl start  rabbitmq-server
-- systemctl enable rabbitmq-server

-- systemctl start  mariadb.service
-- systemctl enable mariadb.service

-- rabbitmqctl add_user mct password
-- rabbitmqctl set_permissions mct ".*" ".*" ".*
