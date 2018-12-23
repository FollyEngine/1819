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

otherPodium = 'podium1'
if myHostname == otherPodium:
    otherPodium = 'podium2'

########################################
# Fire: Attack, Earth: Boost%, Air: Counter, Water: Energy
baselineStats = {'Attack': 10, 'Boost': 100, 'Counter': 15, 'Energy': 40}

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
magic = None    # this is the item element Levels
playerStartState = None
playerCurrentState = None
opponentsCurrent = None
modifier = None
my_magic_cast = None
their_magic_cast = None
combat_round = 0
skip_ABC_reset = 0
def reset():
    state = 'continue-combat'
    if health <= 0:
        global nfcTag
        nfcTag = ''
        global magic
        magic = None
        global playerStartState
        playerStartState = None
        global playerCurrentState
        playerCurrentState = None
        global opponentsCurrent
        opponentsCurrent = None
        global health
        health = 0
        global combat_round
        combat_round = 0
        state = "full-reset"
    global modifier
    modifier = None
    global my_magic_cast
    my_magic_cast = None
    global their_magic_cast
    their_magic_cast = None
    global combat_round
    combat_round = combat_round + 1
    if playerCurrentState != None:
        if skip_ABC_reset > 0:
            global skip_ABC_reset
            skip_ABC_reset = skip_ABC_reset - 1
        else:
            playerCurrentState['Attack'] = playerStartState['Attack']
            playerCurrentState['Boost'] = playerStartState['Boost']
            playerCurrentState['Counter'] = playerStartState['Counter']
        if playerCurrentState['Attack'] == 0 and playerCurrentState['Boost'] == 0 and playerCurrentState['Counter'] == 0:
            play('Dueling/Disable.wav')
    show_health()
    report_state(state)

def report_state(reason):
    print("%s" % reason)
    hostmqtt.publishL(myHostname, DEVICENAME, 'state', {
                    'nfc': nfcTag,
                    'magic': magic,
                    'playerStart': playerStartState,
                    'playerCurrent': playerCurrentState,
                    'opponentsCurrent': opponentsCurrent,
                    'modifier': modifier,
                    'reason': reason,
                    'combat-round': combat_round,
                })
def ive_been_attacked(payload):
    # TODO: not sure if this sound is supposed to happen straight away, or not until both podiums go
    play('TODO - ned to look at the ATK sheet')
def reconcile_magic():
    if my_magic_cast != None and their_magic_cast != None:
        # we use their cast info to determin the effects on us
        if their_magic_cast['modifier'] == 'attack':
            if my_magic_cast['modifier'] == 'counter':
                if playerCurrentState['Counter'] > opponentsCurrent['Energy']:
                    # TODO: not sure 
                    their_magic_cast['Energy'] = opponentsCurrent['Energy'] - playerCurrentState['Counter']
            elif my_magic_cast['modifier'] == 'boost':
                global boost
                boost = 0
            elif my_magic_cast['modifier'] == 'attack':
                if playerCurrentState['Attack'] > opponentsCurrent['Attack']:
                    opponentsCurrent['Energy'] = 0
            playerCurrentState['Energy'] = playerCurrentState['Energy'] - opponentsCurrent['Energy']
        else:
            if my_magic_cast['modifier'] == 'boost':
                #boost attack and counter for next round (or again and again) - again, use the round number
                playerCurrentState['Attack'] = playerCurrentState['Attack'] * playerCurrentState['Boost']
                playerCurrentState['Counter'] = playerCurrentState['Counter'] * playerCurrentState['Boost']
                global skip_ABC_reset
                skip_ABC_reset = 1
        if their_magic_cast['modifier'] == 'disable':
            playerCurrentState['Attack'] = 0
            playerCurrentState['Boost'] = 0
            playerCurrentState['Counter'] = 0
            global skip_ABC_reset
            skip_ABC_reset = 1
        # send player's currentState to other podium
        hostmqtt.publishL(otherPodium, DEVICENAME, 'player-state', playerCurrentState)
        report_state('combat!')
        global health
        health = 100 * playerCurrentState['Energy'] / playerStartState['Energy']
        reset()
        show_health()
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
    global magic
    if payload['nfc'] == nfcTag and magic == None:
        magic = payload
        global playerStartState
        playerStartState['Attack'] = baselineStats['Attack'] * (magic['Fire']*10/100)
        playerStartState['Boost'] = baselineStats['Boost'] * (magic['Earth']*10/100)
        playerStartState['Counter'] = baselineStats['Counter'] * (magic['Air']*10/100)
        playerStartState['Energy'] = baselineStats['Energy'] * (magic['Water']*10/100)
        global playerCurrentState
        playerCurrentState = playerStartState
        # send player's currentState to other podium
        hostmqtt.publishL(otherPodium, DEVICENAME, 'player-state', playerCurrentState)

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
    host, _, _ = topic.split('/')
    if host != myHostname:
        global their_magic_cast
        # TODO: this needs to be the other podium's playerCurrentState
        their_magic_cast = payload
        if payload['modifier'] == 'attack':
            ive_been_attacked(payload)
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

def opponents_state(topic, payload):
    global opponentsCurrent
    opponentsCurrent = payload

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


# send player's currentState to other podium
hostmqtt.subscribeL(myHostname, DEVICENAME, "player-state", opponents_state)

hostmqtt.status({"status": "listening"})

reset()

#try:
hostmqtt.loop_forever()
#except Exception as ex:
#    traceback.print_exc()
#except KeyboardInterrupt:
#    print("exit")

hostmqtt.status({"status": "STOPPED"})