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


# configure mosquitto to relay to mqtt.thegame.folly.site
mosquitto_conf=$(cat <<'END_HEREDOC'
connection folly
address mqtt.thegame.folly.site:8883
topic +/+/+ both
remote_username everyone
remote_password S4C7Tzjc2gD92y9
bridge_insecure true
END_HEREDOC
)

sudo bash -c "echo \"$mosquitto_conf\" > /etc/mosquitto/conf.d/relay.conf"

sudo systemctl stop mosquitto
sudo systemctl start mosquitto
