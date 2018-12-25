# PowerScales Rasberry Pi status


DONE:
* Run main.py on startup
* rename machine to "powerscales" (from health1)
* Continuous Deployment + health ping
.* make a bash script that does mqtt health status ; git pull ; restart buzzwire monitor if new
.* crontab like this
@reboot cd ~/1819 ; rm main_pid
5,10,15,20,25,30,35,40,45,50,55 * * * * cd ~/1819 && ./update.sh >> local.log 2>&1

TODO:



