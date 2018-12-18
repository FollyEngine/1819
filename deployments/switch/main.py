#!/usr/bin/python3
#Copied from DuelingPodium main.py 18/12/28,
# removed lines 95&97 related to the broadcasting of the show health and cast spell functions
# changed DEVICENAME to switch1. No other changes 

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

DEVICENAME="switch1"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

########################################
# on_message subscription functions
displaying = ''
health = 10
def health_calc(host, colour, change = 0):
    global health
    if health < 0:
        health = 15

    if change < 0:
        hostmqtt.publishL(host, 'neopixel', 'play', {
                        'operation': 'health',
                        'count': health,
                        'colour': 'red'
                    })
        health = health + change

    if colour == "off":
        hostmqtt.publishL(host, 'neopixel', 'play', {
                        'operation': 'health',
                        'count': 15,
                        'colour': colour
                    })
    else:
        hostmqtt.publishL(host, 'neopixel', 'play', {
                        'operation': 'health',
                        'count': health,
                        'colour': colour
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

    health_calc(host, colour, 0)

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

    health_calc(host, 'blue', -2)


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

hostmqtt.status({"status": "listening"})

#try:
hostmqtt.loop_forever()
#except Exception as ex:
#    traceback.print_exc()
#except KeyboardInterrupt:
#    print("exit")

hostmqtt.status({"status": "STOPPED"})
