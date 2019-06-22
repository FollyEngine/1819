#!/usr/bin/python3
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
        response = os.system("ping -c 1 " + mqttMasterHost)
        if response == 0:
            break
        logging.info("Waiting for %s: attempt %s"% (mqttMasterHost, i))

hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

########################################
def startServices():
    if myHostname not in hostsConfig:
        logging.log("%s not in hosts config" % (myHostname))
        return
    hostConfig = hostsConfig[myHostname]
    deploymentType = hostConfig["type"]
    deployments = config.getValue("deployments", {})
    for devicename in deployments[deploymentType]:
        t=deployments[deploymentType][devicename]["type"]
        hostmqtt.status({"starting": t})

        cmd = './'+t+'/main.py'
        process = subprocess.Popen(
            ['sudo', cmd, myHostname, deploymentType, devicename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )


########################################
# on_message subscription functions
def msg_update_config(topic, payload):
    logging.info("Received config: %s" % (payload))
    global config
    global hostsConfig
    if mqtt.MQTT.topic_matches_sub(hostmqtt, myHostname+"/"+DEVICENAME+"/update_config", topic):
        logging.info("Setting config")
        # TODO: OMG ew!
        config.cfg = mqtt.get(payload, 'config', {})
        hostsConfig = config.getValue("hosts", {})

hostmqtt.subscribe("update_config", msg_update_config)

hostmqtt.status({"status": "STARTING"})
hostsConfig = config.getValue("hosts", {})
while myHostname not in hostsConfig:
    # request a config from the server
    logging.info("Requesting config")
    hostmqtt.publish("requestconfig", {
        #host type, ip, other things
    })
    time.sleep(5)

logging.info("Starting services")

startServices()

hostmqtt.status({"status": "listening"})

try:
    while True:
        time.sleep(1)
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

hostmqtt.status({"status": "STOPPED"})
