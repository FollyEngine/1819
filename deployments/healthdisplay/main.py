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

DEVICENAME="healthcontroller"

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

########################################
# on_message subscription functions
displaying = False
display = {
    True: 'blue',
    False: 'off'
}
def show_health(topic, payload):
    host, device, verb = topic.split('/')

    global displaying
    displaying = not displaying

    hostmqtt.publishL(host, 'neopixel', 'play', {
                    'operation': 'colorwipe',
                    'colour': display[displaying],
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

hostmqtt.status({"status": "listening"})

try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})