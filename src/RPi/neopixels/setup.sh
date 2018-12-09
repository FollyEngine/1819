#!/bin/bash

cd
if [[ -d rpi_ws2810 ]]; then
	cd rpi_ws281x
	git pull
else
	git clone https://github.com/jgarff/rpi_ws281x
	cd rpi_ws281x
fi


sudo apt-get install scons
scons

cd python
sudo apt-get install python3-dev swig
python3 ./setup.py build
sudo python3 ./setup.py install

