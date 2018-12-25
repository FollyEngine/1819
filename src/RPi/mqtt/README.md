# MQTT server
This is the relay/controller/game engine device
It is the only RPi which is not connected to a thing.
It is the mqtt relay (listening to all devices as well as digitalocean)


DONE:
* Run mqtt on startup
* Continuous Deployment + health ping
.* make a bash script that does mqtt health status ; git pull ; restart buzzwire monitor if new
.* crontab like this
@reboot cd ~/1819 ; rm main_pid
5,10,15,20,25,30,35,40,45,50,55 * * * * cd ~/1819 && ./update.sh >> local.log 2>&1

TODO:
