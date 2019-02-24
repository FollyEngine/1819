#!/bin/bash -ex

# run / setup for the Dueling podium RPi
WHOAMI=$(hostname)
PACKAGES="mqtt megagame rfid-mifare"
MQTTHOST="localhost"
CONFIGFILE=


# Auto start by adding the following to the RPi pi user crontab
# @reboot cd 1819; ./deployments/megagame/run.sh > megagame.log 2>&1


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
			sudo pip install --no-cache-dir -r ./src/RPi/$pkg/requirements.txt
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

for i in $(seq 1 25); do 
	sleep 1
	if [[ $(ping -c 1 "$MQTTHOST") ]]; then 
		break
	fi
done

echo "Starting $WHOAMI"
cd ./src/RPi/

for pkg in $PACKAGES; do
	# TODO: only the remote control and the neopixels need sudo (iirc)
	sudo ./$pkg/main.py > $pkg-${DATE}.log 2>&1 &
done

./../../deployments/megagame/main.py $CONFIGFILE > controller-${DATE}.log 2>&1 &

echo "DONE"
exit
