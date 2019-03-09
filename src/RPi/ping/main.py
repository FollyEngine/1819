#!/usr/bin/python

import time
import sys
import socket
#from subprocess import call
import yaml
import time
from neopixel import *
import argparse
import logging

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt

myHostname = config.getHostname()
deploymenttype=config.getDeploymentType()
DEVICENAME=config.getDevicename()

mqttHost = config.getValue("mqtthostname", "localhost")
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

hostsConfig = config.getValue("hosts", {})
deployments = config.getValue("deployments", {})

logging.info(deployments)

settings = deployments[deploymenttype][DEVICENAME]

logging.info(settings)

############
def get(obj, name, default):
    result = default
    if name in obj:
        result = obj[name]
    return result

########################################
# on_message subscription functions
def msg_play(topic, payload):
    global STATUS
    if mqtt.MQTT.topic_matches_sub(hostmqtt, myHostname+"/"+DEVICENAME+"/reply", topic):
        STATUS = get(payload, 'status', 'red')


STATUS="red"
hostmqtt.subscribe("reply", msg_play)
hostmqtt.status({"status": "listening"})

try:
    while True:
        STATUS="red"
        hostmqtt.publishL("node-red", "status", "ping", {
            "ping": "hello",
            "from": myHostname,
        })
        time.sleep(1)
        hostmqtt.publishL(myHostname, "neopixel-status", "play", {
            "operation": "set",
            "count": 1,
            "colour": STATUS,
        })
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

hostmqtt.status({"status": "STOPPED"})
