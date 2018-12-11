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

DEVICENAME="cauldron"

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

########################################
# on_message subscription functions
displaying = ''
def show_colours(host, colour):
    if change < 0:
        hostmqtt.publishL(host, 'neopixel', 'play', {
                        'operation': 'colourwipe',
                        'colour': colour,
                        'tagid': payload['tag']
                    })

def show_health(topic, payload):
    host, device, verb = topic.split('/')

    global displaying
    if displaying == payload['tag']:
        displaying = ''
        colour = 'off'
    else:
        displaying = payload['tag']
        colour = 'blue'

    show_colours(host, colour)

def cauldron_item(topic, payload):
    if displaying == '':
        # no-one logged on to podium, so no magic happening
        return
    #TODO: add maths that changes the person's health
    host, device, verb = topic.split('/')
    hostmqtt.publishL(host, 'audio', 'play', {
                    'sound': '/usr/share/scratch/Media/Sounds/Effects/Rattle.wav',
                    'tagid': payload['tag']
                })

    show_colours(host, 'green')

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

# cauldron/yellow-rfid/scan {"RSSI": "3b", "time": "2018-12-11T14:18:07.385460", "event": "inserted", "TagPC": "20", "device": "yellow-rfid", "EPC": "3000e200001606180258170069a0", "FreqAnt": "89"}
hostmqtt.subscribeL(myHostname, 'yellow-rfid', "scan", cauldron_item)


hostmqtt.status({"status": "listening"})

try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})