#!/usr/bin/python3

import time
import sys
import socket
#from subprocess import call
import yaml
import time
import argparse
import traceback

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
print(sys.path)
import config
import mqtt
from time import sleep

DEVICENAME='powerscales'

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
########################################
def getHealth(tag, payload):
    payload['A'] = 0
    payload['B'] = 0
    payload['C'] = 0
    payload['D'] = 0
    if tag != "":
        # lookup
        payload['A'] = 3
        payload['B'] = 6
        payload['C'] = 9
        payload['D'] = 1
    return payload
########################################
# on_message subscription functions
displaying = ''
def show_health(topic, payload):
    host, device, verb = topic.split('/')

    global displaying
    if verb == 'removed':
        displaying = ''
    elif displaying == payload['tag']:
        displaying = ''
    else:
        displaying = payload['tag']

    #play({'operation': 'magic_item', "A": 7, "B": 3, "C": 9, "D": 10})
    payload["operation"] = "magic_item"
    payload = getHealth(displaying, payload)
    hostmqtt.publishL(host, 'healthpixels', 'play', payload)

def test_msg(topic, payload):
    #print("Running test_msg")
    hostmqtt.publishL('all', 'healthpixels', 'play', {
                    'operation': 'colorwipe',
                    'colour': 'red',
                    'tagid': 'test'
                })
    hostmqtt.publishL('all', 'healthpixels', 'play', {
                    'operation': 'colorwipe',
                    'colour': 'off',
                    'tagid': 'test'
                })
########################################


# Listen for rfid-nfc scan events
# lookup that tag's health, and send it out to that host's neopixel/play
# wait X seconds, and then turn off.. (or listen for removed event?)

# test signal
hostmqtt.subscribeL("all", DEVICENAME, "test", test_msg)

hostmqtt.subscribeL(myHostname, 'rfid-nfc', "scan", show_health)
hostmqtt.subscribeL(myHostname, 'rfid-nfc', "removed", show_health)

hostmqtt.status({"status": "listening"})

try:
    hostmqtt.loop_forever()
except Exception as ex:
    traceback.print_exc()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})
