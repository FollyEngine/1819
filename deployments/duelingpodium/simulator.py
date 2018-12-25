#!/usr/bin/python3

import datetime
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

DEVICENAME="simulator"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()

def send_nfc(podium, tagid):
    hostmqtt.publishL(podium, "rfid-nfc", "scan", {
            'atr': 'fake',
            'tag': tagid,
            'event': 'inserted'
        })
def send_touch(podium, touch):
    touchname = 'goldpodium'
    if podium == 'podium2':
        touchname = 'silverpodium'
    hostmqtt.publishL('some-esp', touchname, "touch", {
            'atr': 'fake',
            touch: True,
        })
def send_uhf(podium, tagid):
    event = {
        #'data': "%x" % data,
        #'packet_type': packet_type,
        "FreqAnt": 0,
        "TagPC": "fake",
        "tag": tagid,
        "rssi": 50,
        'event': 'inserted'
    }
    hostmqtt.publishL(podium, "yellow-rfid", "scan", event)

wands = {
    'CB774FEC': '3000e20000167303013123202a5a', #svens wand
}

# all alone, no combat happens
send_uhf('podium1', '3000e20000167303013123202a5a')

time.sleep(1)

send_nfc('podium1', 'CB774FEC')
send_uhf('podium1', '3000e20000167303013123202a5a')

time.sleep(1)
send_touch('podium1', 'touch7')
send_uhf('podium1', '3000e20000167303013123202a5a')

time.sleep(1)

send_nfc('podium1', 'CB774FEC')


try:
    while True:
        time.sleep(1)
except Exception as ex:
    traceback.print_exc()
except KeyboardInterrupt:
    print("exit")
