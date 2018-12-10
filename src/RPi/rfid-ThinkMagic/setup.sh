#!/bin/bash


sudo pip3 install --no-cache-dir -r ./src/RPi/rfid-ThinkMagic/requirements.txt

cd
if [[ -d python-mercuryapi ]]; then
	cd python-mercuryapi
	git pull
else
	git clone https://github.com/gotthardp/python-mercuryapi
	cd python-mercuryapi
fi


apt-get install patch xsltproc gcc libreadline-dev python-dev python-setuptools
make
sudo make install

sudo usermod -a -G dialout $USER
