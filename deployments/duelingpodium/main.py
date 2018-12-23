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

DEVICENAME="podium"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

########################################
def play(sound):
    hostmqtt.publishL(myHostname, 'audio', 'play', {
                    'sound': sound,
                    #'tagid': payload['tag']
                })
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
my_magic_cast = None
their_magic_cast = None
disable_next_round = False
def reset():
    state = 'continue-combat'
    if health <= 0:
        global nfcTag
        nfcTag = ''
        global magic
        magic = None
        global health
        health = 0
        state = "full-reset"
    else:
        # TODO: how to deal with disable_next_round
        global disable_next_round
        disable_next_round = False
    global modifier
    modifier = None
    global my_magic_cast
    my_magic_cast = None
    global their_magic_cast
    their_magic_cast = None
    show_health()
    report_state(state)

def report_state(reason):
    print("%s" % reason)
    hostmqtt.publishL(myHostname, DEVICENAME, 'state', {
                    'nfc': nfcTag,
                    'magic': magic,
                    'modifier': modifier,
                    'reason': reason,
                })
def ive_been_attacked(payload):
    # TODO: not sure if this sound is supposed to happen straight away, or not until both podiums go
    play('TODO - ned to look at the ATK sheet')
def reconcile_magic():
    if my_magic_cast != None and their_magic_cast != None:
        # this is the place where we figure out the consequences
        report_state('combat!')
    # TODO: how to start the timeout....
########################################
# on_message subscription functions
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

def read_nfc(topic, payload):
    host, device, verb = topic.split('/')

    global nfcTag
    if nfcTag == payload['tag']:
        reset()
        report_state('remove-nfc')
    else:
        nfcTag = payload['tag']
        report_state('set-nfc')
        play('Dueling/Magic Detected.mp3')

# info from the database
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
        # if its for the other podium, we could use it - but it could also be for the cauldron
        report_state('not-my-magic-stats')

touches = {
#| battle amulet     |function | touch number ||
#| flower             | boost   | touch0       |
#| diamond stone      | attack  | touch7       |
#| brass shell        | counter | touch5       |
#| multifaceted stone | disable (debuff)  | touch3       |
    'touch0': 'boost',
    'touch6': 'attack',     # blackpodium
    'touch7': 'attack',      # silverpodium and goldpodium
    'touch5': 'counter',
    'touch3': 'disable',
}
def set_modifier(topic, payload):
    global modifier
    mod = None
    for t in touches.keys():
        if t in payload:
            if payload[t] == True:
                if mod != None:
                    # if they're holding more than one, then they're not ready to cast
                    modifier = None
                    report_state('more-than-one-modifier-touched')
                    return
                mod = touches[t]
    modifier = mod
    if modifier == None:
        report_state('no-modifier')
    else:
        report_state('modifier-ready')

def magic_cast(topic, payload):
    host, device, verb = topic.split('/')
    if host != myHostname:
        global their_magic_cast
        their_magic_cast = payload
        if payload['modifier'] == 'attack':
            ive_been_attacked(payload)
        elif payload['modifier'] == 'disable':
            global disable_next_round
            disable_next_round = True
    else:
        global my_magic_cast
        my_magic_cast = payload
        if payload['modifier'] == 'boost':
            play('Dueling/Boost.wav')
        elif payload['modifier'] == 'counter':
            play('Dueling/Counter.wav')
        elif payload['modifier'] == 'disable':
            play('Dueling/Disable.wav')
    reconcile_magic()

def read_uhf(topic, payload):
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
    hostmqtt.publishL(myHostname, DEVICENAME, 'magic_cast', {
                    'nfc': nfcTag,
                    'magic': magic,
                    'modifier': modifier,
                })
    report_state('uhf-cast-magic')
    

########################################


# Listen for rfid-nfc scan events
# lookup that tag's health, and send it out to that host's neopixel/play
# wait X seconds, and then turn off.. (or listen for removed event?)

# test signal
hostmqtt.subscribeL("all", DEVICENAME, "test", test_msg)

hostmqtt.subscribeL(myHostname, 'rfid-nfc', "scan", read_nfc)
hostmqtt.subscribeL('all', 'db_lookup', 'magic-item', get_magic)
hostmqtt.subscribeL('+', 'blackpodium', 'touch', set_modifier)
hostmqtt.subscribeL(myHostname, 'yellow-rfid', "scan", read_uhf)
hostmqtt.subscribeL('+', DEVICENAME, "magic_cast", magic_cast)

hostmqtt.status({"status": "listening"})

reset()

#try:
hostmqtt.loop_forever()
#except Exception as ex:
#    traceback.print_exc()
#except KeyboardInterrupt:
#    print("exit")

hostmqtt.status({"status": "STOPPED"})