#!/usr/bin/python3

import time
import sys
import socket
#from subprocess import call
import yaml
import time
#from neopixel import *
#from adafruit_crickit import crickit
#from adafruit_seesaw.neopixel import NeoPixel
import argparse
import logging

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt
sys.path.append('./crickit/')
import myneopixels


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

# TODO: should get default from DEVICE type, and then over-ride from host settings
#num_pixels = 64  # Number of pixels driven from Crickit NeoPixel terminal
#pixels = NeoPixel(crickit.seesaw, 20, num_pixels)
pixels = myneopixels.MyNeoPixels(64)
pixels.fill(myneopixels.colors['off'])

# can do things like:
#  mosquitto_pub -h mqtt -t two/neopixel/play -m '{"operation": "theatrechase", "colour": "green"}'

############

########################################
# on_message subscription functions
def msg_play(topic, payload):
    if mqtt.MQTT.topic_matches_sub(hostmqtt, "all/"+DEVICENAME+"/play", topic):
        # everyone
        #logging.info("everyone plays "+payload)
        pixels.play(payload)
    elif mqtt.MQTT.topic_matches_sub(hostmqtt, myHostname+"/"+DEVICENAME+"/play", topic):
        #logging.info(myHostname+" got "+payload+" SPARKLES!!")
        pixels.play(payload)

def msg_test(topic, payload):
    pixels.play({'operation': 'colourwipe', 'colour': 'yellow'})

def msg_combat_end(topic, payload):
    colourname = myneopixels.get(payload, 'colour', 'yellow')
    count = myneopixels.get(payload, 'count', 1)
    for i in range(0, count):
        pixels.play({'operation': 'colourwipe', 'colour': colourname})
        pixels.play({'operation': 'colourwipe', 'colour': 'off'})


hostmqtt.subscribe("play", msg_play)
hostmqtt.subscribeL("all", DEVICENAME, "play", msg_play)
hostmqtt.subscribeL("all", DEVICENAME, "test", msg_test)

hostmqtt.subscribeL(myHostname, DEVICENAME, "combat-end", msg_combat_end)

hostmqtt.status({"status": "listening"})
msg_combat_end('one/two/three', {'colour': 'red', 'count': 1})
hostmqtt.publish('combat-end', {'colour': 'yellow', 'count': 1})

try:
    while True:
        time.sleep(1)
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

pixels.fill(myneopixels.colors['off'])
hostmqtt.status({"status": "STOPPED"})
