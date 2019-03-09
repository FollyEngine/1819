#!/usr/bin/python
#
# run.py reads the config.yml, 
# and uses that to decide what services to start

import yaml
import time
import argparse
import logging
import os

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt
import subprocess

DEVICENAME="deployment"
myHostname = config.getHostname(False)

mqttHost = config.getValue("mqtthostname", "localhost")
for i in range(0, 25):
    time.sleep(1)
    response = os.system("ping -c 1 " + mqttHost)
    if response == 0:
        break
    logging.info("Waiting for %s: attempt %s"% (mqttHost, i))

mqttMasterHost = config.getValue("mqttmaster", "")
if mqttMasterHost != "":
    for i in range(0, 25):
        time.sleep(1)
        response = os.system("ping -c 1 " + mqttHost)
        if response == 0:
            break
        logging.info("Waiting for %s: attempt %s"% (mqttHost, i))

hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

hostsConfig = config.getValue("hosts", {})
hostConfig = hostsConfig[myHostname]
deploymentType = hostConfig["type"]
deployments = config.getValue("deployments", {})

hostmqtt.status({"status": "STARTING"})


for devicename in deployments[deploymentType]:
    t=deployments[deploymentType][devicename]["type"]
    hostmqtt.status({"starting": t})

    cmd = './'+t+'/main.py'
    process = subprocess.Popen(['sudo', cmd, myHostname, deploymentType, devicename],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    )

hostmqtt.status({"status": "STOPPED"})
