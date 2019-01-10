# SecretSwitch Rasberry Pi status
This is a button (or something) that a character has in their pocket (or somewhere).
it's the simplest one.

DONE:

TODO:
- update git to point to github instead of sven's place
* Connect through telstra dongle
.* SSID TPU4G_????
.* pwd ???????
.* edit /etc/wpa_supplicant/wpa_supplicant.conf  :  add SSID/psk above and add "priority 1"
* Run secretswitch monitor on startup
* rename machine to "secretswitch" (from switch2)
* Continuous Deployment + health ping
.* make a bash script that does mqtt health status ; git pull ; restart buzzwire monitor if new
.* crontab like this
@reboot cd ~/1819 ; rm main_pid
5,10,15,20,25,30,35,40,45,50,55 * * * * cd ~/1819 && ./update.sh >> local.log 2>&1



NOTE : whichever dongle has SSID TPU4G_T39Y has psk 63619637