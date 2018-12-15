#!/bin/bash -x


sudo pip install --no-cache-dir -r ./src/RPi/rfid-ThinkMagic/requirements.txt
sudo pip3 install --no-cache-dir -r ./src/RPi/rfid-ThinkMagic/requirements.txt

cd
if [[ -d python-mercuryapi ]]; then
	cd python-mercuryapi
	git pull
else
	git clone https://github.com/gotthardp/python-mercuryapi
	cd python-mercuryapi
fi


sudo apt-get install -yq patch xsltproc gcc libreadline-dev python-dev python-setuptools python3-dev
make PYTHON=python
sudo python setup.py install
make PYTHON=python3
sudo python3 setup.py install


sudo usermod -a -G dialout $USER
