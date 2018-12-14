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
import config
import mqtt
from time import sleep

DEVICENAME="cauldron"

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

########################################
# on_message subscription functions
displaying = ''
def show_colours(host, colour):
    hostmqtt.publishL(host, 'neopixel', 'play', {
                    'operation': 'colourwipe',
                    'colour': colour
                })

def show_magic_colours(host, A, B, C, D):
    hostmqtt.publishL(host, 'neopixel', 'play', {
                    'operation': 'magic_item',
                    'A': A,
                    'B': B,
                    'C': C,
                    'D': D
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

wandTags = {
    # the 4 tire tags
    "3000e2000016630301560190f4bf": "",
    "3000e200001673030216183059fe": "",
    "3000e2000016730602271180a23f": "",
    "3000e20000167303013123202a5a": ""
}
ingredients = {
    "0": {'A': 0, 'B': 0, 'C': 1, 'D': 0},
    "1": {'A': 5, 'B': 0, 'C': 0, 'D': 1},
    "2": {'A': 0, 'B': 2, 'C': 4, 'D': 0},
    "3": {'A': 3, 'B': 0, 'C': 0, 'D': 2},
    "4": {'A': 0, 'B': 4, 'C': 7, 'D': 0},
    "5": {'A': 1, 'B': 0, 'C': 0, 'D': 3},
    "6": {'A': 0, 'B': 6, 'C': 9, 'D': 0},
    "7": {'A': 7, 'B': 0, 'C': 0, 'D': 7},
    "8": {'A': 0, 'B': 9, 'C': 3, 'D': 0},
    "9": {'A': 5, 'B': 0, 'C': 0, 'D': 9},
}
index = 0
A = 0   # Attack
B = 0   # Buff
C = 0   # Counter
D = 0   # Debuff

def cauldron_item(topic, payload):
    global A, B, C, D, index
    #TODO: add maths that changes the person's health
    host, device, verb = topic.split('/')

    if payload['tag'] in wandTags:
        # loading the wand / orb / item with the current magic
        hostmqtt.publishL("all", 'magic', 'set', {
                        'tagid': payload['tag'],
                        'A': A,
                        'B': B,
                        'C': C,
                        'D': D
                    })
        A = 0
        B = 0
        C = 0
        D = 0
        show_colours(host, 'off')
        hostmqtt.publishL(host, 'audio', 'play', {
                        'sound': '/usr/share/scratch/Media/Sounds/Effects/Pop.wav',
                        'tagid': payload['tag']
                    })
    else:
        i = "%d" % index
        A = A + ingredients[i]['A']
        B = B + ingredients[i]['B']
        C = C + ingredients[i]['C']
        D = D + ingredients[i]['D']
        index = index + 1
        if index > 9:
            index = 0
        hostmqtt.publishL(host, 'audio', 'play', {
                        'sound': '/usr/share/scratch/Media/Sounds/Effects/Rattle.wav',
                        'tagid': payload['tag']
                    })
        show_magic_colours(host, A, B, C, D)

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
except Exception as ex:
    traceback.print_exc()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})