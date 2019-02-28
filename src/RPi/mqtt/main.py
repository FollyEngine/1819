#!//usr/bin/python3
# This is the mqtt relay, which listens to all the devices and the remote mqtt server and relays & responds to subscriptions

### BUT FIRST
# this RPi also owns the database.  start that
#import subprocess
#subprocess.Popen(['nohup', 'database/main.py'])

import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
import logging
from time import sleep

allMuted = False
repeats = {}

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import mqtt
import config

sleep(5)

myHostname = config.getHostname()
deploymenttype=config.getDeploymentType()
DEVICENAME=config.getDevicename()

mqttHost = config.getValue("mqtthostname", "localhost")
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

master_mqtt_host = config.getValue("mqttmaster", "mqtt.thegame.folly.site")
mastermqtt = mqtt.MQTT(master_mqtt_host, myHostname, "relay_to", "everyone", "S4C7Tzjc2gD92y9", 8883)
#mastermqtt.loop_start()   # use the background thread

# end load config

############
def muteAll():
    hostmqtt.publishL("all", "audio", "mute", {})

########################################################
# subscription handlers

def relay_message_to_master(topic, payload):
    try:
        # Only relay messages from our local mqtt to the global one if they havn't already been relayed
        if "relay_from" in payload:
            #logging.info("relayed before "+payload["relay_from"])
            return

        payload["relay_from"] = myHostname
        logging.info("Relaying to master: %s, %s" % (topic, payload))
        mastermqtt.relay(topic, payload)
    except Exception as ex:
        logging.error("Exception occurred", exc_info=True)


def relay_message_from_master(topic, payload):
    try:
        # Only relay messages from our local mqtt to the global one if they havn't already been relayed
        if not "relay_from" in payload:
            payload["relay_from"] = master_mqtt_host
        else:
            if payload["relay_from"] == myHostname:
                # don't relay a message that originated with us...
                return

        logging.info("Relaying from master: %s, %s" % (topic, payload))
        hostmqtt.relay(topic, payload)
    except Exception as ex:
        logging.error("Exception occurred", exc_info=True)

########################################


hostmqtt.subscribeL("+", "+", "+", relay_message_to_master)
logging.info(hostmqtt.sub)
mastermqtt.subscribeL("+", "+", "+", relay_message_from_master)

hostmqtt.status({"status": "listening"})
mastermqtt.status({"status": "listening"})

try:
    #while True:
    #    sleep(1)
    mastermqtt.loop_forever()
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

hostmqtt.status({"status": "STOPPED"})
mastermqtt.status({"status": "STOPPED"})
