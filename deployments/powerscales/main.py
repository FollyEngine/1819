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
# on_message subscription functions
displaying = ''
def show_health(topic, payload):
    host, device, verb = topic.split('/')

    global displaying
    if verb == 'removed':
        displaying = ''
        hostmqtt.publishL(myHostname, 'healthpixels', 'play', {'reason': 'tag-off', operation': 'magic_item', "Air": 0, "Fire": 0, "Water": 0, "Earth": 0})
    elif displaying == payload['tag']:
        displaying = ''
        hostmqtt.publishL(myHostname, 'healthpixels', 'play', {'reason': 'tag-off', operation': 'magic_item', "Air": 0, "Fire": 0, "Water": 0, "Earth": 0})
    else:
        displaying = payload['tag']

def get_magic(topic, payload):
    global magic
    if payload['nfc'] == displaying:
        magic = payload
        payload["operation"] = "magic_item"
        hostmqtt.publishL(myHostname, 'healthpixels', 'play', payload)


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

hostmqtt.subscribeL('all', 'db_lookup', 'magic-item', get_magic)

hostmqtt.status({"status": "listening"})

try:
    hostmqtt.loop_forever()
except Exception as ex:
    traceback.print_exc()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})
