#!/bin/bash -ex

# run / setup for the Dueling podium RPi
WHOAMI=$(hostname)
PACKAGES="audio mqtt neopixels rfid-ThinkMagic rfid-mifare"
MQTTHOST="mqtt"
CONFIGFILE=


# Auto start by adding the following to the RPi pi user crontab
# @reboot cd 1819; ./deployments/duelingpodium/run.sh > duelingpodium.log 2>&1


echo "$WHOAMI in $(pwd)"
echo "talking to message queue server: $MQTTHOST"
echo "packages: $PACKAGES"

if [[ ¨$1¨ == ¨--setup¨ ]]; then
	echo "Running Setup"
	# get pyscard
	sudo apt-get update
	sudo apt-get upgrade -yq
	sudo apt-get install -yq python3-pyscard python3-pip pcsc-tools pcscd git python3-setuptools libpcsclite-dev python3-dev \
				mosquitto-clients mosquitto scratch python-pygame

	git pull

	for pkg in $PACKAGES; do
		if [[ -f "./src/RPi/$pkg/requirements.txt" ]]; then
			sudo pip3 install --no-cache-dir -r ./src/RPi/$pkg/requirements.txt
		fi
		if [[ -f "./src/RPi/$pkg/setup.sh" ]]; then
			./src/RPi/$pkg/setup.sh
		fi
	done

	cat /proc/device-tree/model
	if grep "Raspberry Pi" /proc/device-tree/model; then
		if ! lsmod | grep hifiberry; then
			echo "installing drivers for pHAT"
			curl https://get.pimoroni.com/phatdac | bash
		fi
	fi
	exit
fi

sleep 15
ping -c 1 $MQTTHOST

echo "Starting $WHOAMI"
cd ./src/RPi/

for pkg in $PACKAGES; do
	# TODO: the remote control and the neopixels, rfid-mifare need sudo (iirc)
	if [[ "$pkg" == "rfid-ThinkMagic" ]]; then
		./while.sh sudo ./$pkg/main.py > $pkg-${DATE}.log 2>&1 &
	else
		sudo ./$pkg/main.py > $pkg-${DATE}.log 2>&1 &
	fi
done

./../../deployments/duelingpodium/main.py $CONFIGFILE > controller-${DATE}.log 2>&1 &

echo "DONE"
exit
