# BuzzSwitch Rasberry Pi status

DONE:
- update git to point to github instead of sven's place
* Connect through telstra dongle
.* SSID TPU4G_6GN6
.* pwd 70253140
.* edit /etc/wpa_supplicant/wpa_supplicant.conf  :  add SSID/psk above and add "priority 1"
* Run buzzswitch monitor on startup
* rename machine to "buzzswitch" (from switch2)

TODO:
* Continuous Deployment + health ping
.* make a bash script that does mqtt health status ; git pull ; restart buzzswitch monitor if new
.* crontab like this
  0/5 * * * * cd 1819 && update.sh > local.log 2>&1


NOTE : whichever dongle has SSID TPU4G_T39Y has psk 63619637