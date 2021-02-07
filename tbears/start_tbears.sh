#!/bin/bash

tbears stop
sudo service rabbitmq-server start
pkill gunicorn
tbears start -c ./config/iconsafe/localhost/tbears_server_config.json
