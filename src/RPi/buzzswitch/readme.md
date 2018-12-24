# BuzzSwitch Rasberry Pi status

DONE:
- update git to point to github instead of sven's place
* Connect through telstra dongle
.* SSID TPU4G_6GN6
.* pwd 70253140
.* edit /etc/wpa_supplicant/wpa_supplicant.conf  :  add SSID/psk above and add "priority 1"
* Run buzzswitch monitor on startup
* rename machine to "buzzswitch" (from switch2)
* Continuous Deployment + health ping
.* make a bash script that does mqtt health status ; git pull ; restart buzzswitch monitor if new
.* crontab like this
  @reboot cd ~/1819 ; rm main_pid
  5,10,15,20,25,30,35,40,45,50,55 * * * * cd ~/1819 && ./update.sh >> local.log 2>&1

TODO:
nothing!

NOTE : whichever dongle has SSID TPU4G_T39Y has psk 63619637