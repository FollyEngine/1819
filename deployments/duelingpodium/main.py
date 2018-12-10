#!/usr/bin/python3

import time
import sys
import socket
#from subprocess import call
import yaml
import time
import argparse

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt

DEVICENAME="podium"

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

########################################
# on_message subscription functions
displaying = ''
def show_health(topic, payload):
    host, device, verb = topic.split('/')

    global displaying
    if displaying == payload['tag']:
        displaying = ''
        colour = 'off'
    else:
        displaying = payload['tag']
        colour = 'blue'

    hostmqtt.publishL(host, 'neopixel', 'play', {
                    'operation': 'colorwipe',
                    'colour': colour,
                    'tagid': payload['tag']
                })

def magic_cast(topic, payload):
    if displaying == '':
        # no-one logged on to podium, so no magic happening
        return
    #TODO: add maths that changes the person's health
    host, device, verb = topic.split('/')
    hostmqtt.publishL(host, 'audio', 'play', {
                    'sound': '/usr/share/scratch/Media/Sounds/Effects/Rattle.wav',
                    'tagid': payload['tag']
                })

def test_msg(topic, payload):
    hostmqtt.publishL('all', 'neopixel', 'play', {
                    'operation': 'colorwipe',
                    'colour': 'red',
                    'tagid': 'test'
                })
    hostmqtt.publishL('all', 'neopixel', 'play', {
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

hostmqtt.subscribeL(myHostname, 'ThingMagic', "scan", magic_cast)


hostmqtt.status({"status": "listening"})

try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})