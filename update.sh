#!/bin/bash
git pull
python ./src/RPi/$HOSTNAME/main.py
##  this "healthy" report just says that we're turned on and online.  
## TODO : check whether the python script is actually running without error
## TODO : report when an update has occurred
mosquitto_pub -h "mqtt.thegame.folly.site"  -u mqtt.thegame.folly.site -P S4C7Tzjc2gD92y9  -t "$HOSTNAME/$HOSTNAME/status" -m '{"status":"healthy"}'