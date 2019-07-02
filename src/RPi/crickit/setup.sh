#!/bin/bash



#https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
sudo apt-get install -yq python-smbus i2c-tools

# lets see if its there
sudo i2cdetect -y 1

# https://learn.adafruit.com/adafruit-crickit-hat-for-raspberry-pi-linux-computers?view=all#install-adafruit-blinka-enable-i2c-9-2

sudo apt-get install -y python3 git python3-pip
#sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.5 2
sudo update-alternatives --config python

sudo pip3 install --no-cache-dir -r ./src/RPi/crickit/requirements.txt
