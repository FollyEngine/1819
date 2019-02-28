#!/usr/bin/python
#
# run.py reads the config.yml, 
# and uses that to decide what services to start

import socket
import yaml
import time
import argparse
import traceback

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import subprocess

DEVICENAME="deployment"

mqttHost = config.getValue("mqtthostname", "localhost")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

hostsConfig = config.getValue("hosts", {})
hostConfig = hostsConfig[myHostname]
deploymentType = hostConfig["type"]
deployments = config.getValue("deployments", {})

for devicename in deployments[deploymentType]:
    print(devicename)
    t=deployments[deploymentType][devicename]["type"]

    cmd = './'+t+'/main.py'
    process = subprocess.Popen(['sudo', cmd, myHostname, deploymentType, devicename])
