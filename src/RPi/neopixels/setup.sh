#!/bin/bash


sudo pip install --no-cache-dir -r ./src/RPi/neopixels/requirements.txt
sudo pip3 install --no-cache-dir -r ./src/RPi/neopixels/requirements.txt

cd
if [[ -d rpi_ws2810 ]]; then
	cd rpi_ws281x
	git pull
else
	git clone https://github.com/jgarff/rpi_ws281x
	cd rpi_ws281x
fi


sudo apt-get install -yq scons gcc
scons

cd python
sudo apt-get install -yq python3-dev swig python-dev
python ./setup.py build
sudo python ./setup.py install

python3 ./setup.py build
sudo python3 ./setup.py install

