#!/bin/bash
# If the main process (main.py) belonging to this host is not running, start it.
# If that script has been updated in github, restart it.
# To make this work, add these two lines to your crontab (crontab -e)
# @reboot cd ~/1819 ; rm main_pid
# 5,10,15,20,25,30,35,40,45,50,55 * * * * cd ~/1819 && ./update.sh >> local.log 2>&1


## This script requires that main_pid does not exist on system start.
if [ ! -f main_pid ] ; then
  pip install --no-cache-dir -r ./src/RPi/$HOSTNAME/requirements.txt

  cd src/RPi && nohup python ./$HOSTNAME/main.py &
  mosquitto_pub -h "mqtt.thegame.folly.site"  -u mqtt.thegame.folly.site -P S4C7Tzjc2gD92y9  -t "$HOSTNAME/$HOSTNAME/health" -m "{\"status\":\"started\",\"time\":\"$(date +%Y-%m-%dZ%H:%M:%S)\",\"device\":\"$HOSTNAME $(hostname -I)\"}"
  echo $! > main_pid
fi
# Update repository, and if our main file has changed, restart it
OLD_HEAD=$(git rev-parse HEAD)
git pull
NEW_HEAD=$(git rev-parse HEAD)
git diff --name-only $OLD_HEAD $NEW_HEAD ./src/RPi/$HOSTNAME/main.py | grep main.py
gitstatus = $?
echo "status of that grep $gitstatus" 
if [ ! gitstatus ] ; then
  # our main file was updated.  kill the running one and start a new one
    kill $(cat main_pid)
    cd src/RPi && nohup python ./$HOSTNAME/main.py &
    echo $! > main_pid
    mosquitto_pub -h "mqtt.thegame.folly.site"  -u mqtt.thegame.folly.site -P S4C7Tzjc2gD92y9  -t "$HOSTNAME/$HOSTNAME/health" -m "{\"status\":\"updated\",\"time\":\"$(date +%Y-%m-%dZ%H:%M:%S)\",\"device\":\"$HOSTNAME $(hostname -I)\"}"
fi

sync
##  this "healthy" report just says that we're turned on and online.  
## TODO : check whether the python script is actually running without error
## TODO : report when an update has occurred
mosquitto_pub -h "mqtt.thegame.folly.site"  -u mqtt.thegame.folly.site -P S4C7Tzjc2gD92y9  -t "$HOSTNAME/$HOSTNAME/health" -m "{\"status\":\"healthy\",\"time\":\"$(date +%Y-%m-%dZ%H:%M:%S)\",\"device\":\"$HOSTNAME\"}"
