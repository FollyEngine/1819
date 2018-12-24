#!/bin/bash
# Update repository, and if our main file has changed, restart it
OLD_HEAD=$(git rev-parse HEAD)
git pull
NEW_HEAD=$(git rev-parse HEAD)
git diff --name-only $OLD_HEAD $NEW_HEAD ./src/RPi/$HOSTNAME/main.py | grep main.py
if [ ! $? ] ; then
  # our main file was updated.  kill the running one and start a new one
    kill $(cat main_pid)
    nohup python ./src/RPi/$HOSTNAME/main.py &
    echo $! > main_pid
fi

##  this "healthy" report just says that we're turned on and online.  
## TODO : check whether the python script is actually running without error
## TODO : report when an update has occurred
mosquitto_pub -h "mqtt.thegame.folly.site"  -u mqtt.thegame.folly.site -P S4C7Tzjc2gD92y9  -t "$HOSTNAME/$HOSTNAME/status" -m '{"status":"healthy"}'