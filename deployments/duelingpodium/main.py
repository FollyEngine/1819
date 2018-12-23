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

DEVICENAME="podium"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

########################################
health = 100
def show_health():
    hostmqtt.publishL(myHostname, 'neopixel', 'play', {
                    'operation': 'health',
                    'count': health,
                    'colour': 'blue'
                })


nfcTag = ''
magic = None
modifier = None
def reset():
    global nfcTag
    nfcTag = ''
    global magic
    magic = None
    global modifier
    modifier = None
    hostmqtt.publishL(myHostname, 'neopixel', 'play', {
                    'operation': 'health',
                    'count': 0,
                })
    report_state("reset")

def report_state(reason):
    print("%s" % reason)
    hostmqtt.publishL(myHostname, DEVICENAME, 'state', {
                    'nfc': nfcTag,
                    'magic': magic,
                    'modifier': modifier,
                    'reason': reason,
                })

########################################
# on_message subscription functions
def read_nfc(topic, payload):
    host, device, verb = topic.split('/')

    global nfcTag
    if nfcTag == payload['tag']:
        reset()
        report_state('remove-nfc')
    else:
        nfcTag = payload['tag']
        report_state('set-nfc')


def magic_cast(topic, payload):
    if nfcTag == '':
        # no-one logged on to podium, so no magic happening
        report_state('uhf-no-nfc')
        return
    if magic == None:
        report_state('uhf-no-database')
        return
    if modifier == None:
        report_state('uhf-no-modifier')
        return
    #TODO: add maths that changes the person's health
    host, device, verb = topic.split('/')
    hostmqtt.publishL(host, 'audio', 'play', {
                    'sound': '/usr/share/scratch/Media/Sounds/Effects/Rattle.wav',
                    'tagid': payload['tag']
                })

    # TODO: need to wait for other side, then figure out how won, and then do consequenses
    global health
    health = health - 2
    report_state('uhf-cast-magic')
    show_health()


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

def get_magic(topic, payload):
    #{"Earth": 10, 
    # "time": "2018-12-22T20:43:40.715609", 
    # "nfc": "550A5CBC", 
    # "Fire": 10, 
    # "Air": 10, 
    # "Water": 10, 
    # "id": 4, 
    # "uhf": "3000e200001606180258170069a0", 
    # "name": "", 
    # "device": "db_lookup"}
    if payload['nfc'] == nfcTag:
        global magic
        magic = payload
        show_health()
        report_state('set-magic-stats')
    else:
        report_state('not-my-magic-stats')


def set_modifier(topic, payload):
    global modifier
    mod = None
    for t in ['touch0', 'touch3', 'touch5', 'touch6']:
        if t in payload:
            if payload[t] == True:
                if mod != None:
                    # if they're holding more than one, then they're not ready to cast
                    modifier = None
                    report_state('more-than-one-modifier-touched')
                    return
                mod = t
    modifier = mod
    report_state('modifier-ready')
########################################


# Listen for rfid-nfc scan events
# lookup that tag's health, and send it out to that host's neopixel/play
# wait X seconds, and then turn off.. (or listen for removed event?)

# test signal
hostmqtt.subscribeL("all", DEVICENAME, "test", test_msg)

hostmqtt.subscribeL(myHostname, 'rfid-nfc', "scan", read_nfc)
hostmqtt.subscribeL('all', 'db_lookup', 'magic-item', get_magic)
hostmqtt.subscribeL('+', 'blackpodium', 'touch', set_modifier)
hostmqtt.subscribeL(myHostname, 'yellow-rfid', "scan", magic_cast)

hostmqtt.status({"status": "listening"})

reset()

#try:
hostmqtt.loop_forever()
#except Exception as ex:
#    traceback.print_exc()
#except KeyboardInterrupt:
#    print("exit")

hostmqtt.status({"status": "STOPPED"})