#!/bin/bash -ex

PACKAGES="audio mqtt neopixels rfid-d10x rfid-mifare"

echo "Running Setup"
# get pyscard
sudo apt-get update
sudo apt-get upgrade -yq
sudo apt-get install -yq python3-pyscard python3-pip pcsc-tools pcscd git python3-setuptools libpcsclite-dev python3-dev \
			mosquitto-clients mosquitto scratch python-pygame \
			python3-serial python-serial python-pip python-pyscard \
			vim comitup

git pull

for pkg in $PACKAGES; do
	if [[ -f "./src/RPi/$pkg/requirements.txt" ]]; then
		sudo pip install --no-cache-dir -r ./src/RPi/$pkg/requirements.txt
		sudo pip3 install --no-cache-dir -r ./src/RPi/$pkg/requirements.txt
	fi
	if [[ -f "./src/RPi/$pkg/setup.sh" ]]; then
		./src/RPi/$pkg/setup.sh
	fi
done

crontab cron.load


# configure mosquitto to relay to mqtt.thegame.folly.site
mosquitto_conf=$(cat <<'END_HEREDOC'
connection folly
address mqtt.thegame.folly.site:8883
topic +/+/+ both
remote_username EDITME
remote_password EDITME
bridge_insecure true
END_HEREDOC
)

sudo bash -c "echo \"$mosquitto_conf\" > /etc/mosquitto/conf.d/relay.conf"

sudo systemctl stop mosquitto
sudo systemctl start mosquitto

# this needs to be last - it wants to reboot
cat /proc/device-tree/model
if grep "Raspberry Pi" /proc/device-tree/model; then
	if ! lsmod | grep hifiberry; then
		echo "installing drivers for pHAT"
		curl https://get.pimoroni.com/phatdac | bash
	fi
fi
exit
