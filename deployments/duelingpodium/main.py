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
#import pysimpledmx


# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt

DEVICENAME="podium"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

#mydmx = pysimpledmx.DMXConnection("/dev/ttyUSB1")

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
health = 0
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
    global health
    global combat_round
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
        health = 0
        combat_round = 0
        state = "full-reset"
    global modifier
    modifier = None
    global my_magic_cast
    my_magic_cast = None
    global their_magic_cast
    their_magic_cast = None
    combat_round = combat_round + 1
    if playerCurrentState != None:
        global skip_ABC_reset
        if skip_ABC_reset > 0:
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

#	F	    E	    W	    A
#F	Fire	Lava	Steam	Lightning
#E	Lava	Earth	Wood	Dust
#W	Steam	Wood	Water	Ice
#A	Lightning	Dust	Ice	Air
#Elements		F	E	W	A	F	F	E	F	E	W	
#Elements		F	E	W	A	E	W	W	A	A	A	Balanced
#Spell		Fire	Earth	Water	Air	  Lava	    Steam	Wood	Electricity	Dust	Ice	Light
#LED1	RED	GREEN	BLUE	WHITE	RED	    RED	    GREEN	RED	GREEN	BLUE	AMBER
#	2	RED	GREEN	BLUE	WHITE	GREEN   BLUE	BLUE	WHITE	WHITE	WHITE	AMBER
#	3	RED	GREEN	BLUE	WHITE	RED	    RED	    GREEN	RED	GREEN	BLUE	AMBER
#	4	RED	GREEN	BLUE	WHITE	GREEN   BLUE	BLUE	WHITE	WHITE	WHITE	AMBER
#Sound	Fire.wav	ATK - Earth.wav	ATK - Water.mp3	ATK - Air.mp3	STK - Lava.wav	ATK - Steam.wav	AK - Wood.wav	ATK - Lightning.wav	ATK - Sand.wav	ATK - Ice.mp3	ATK - Light.wav
spellSounds = {
"Steam": "Dueling/ATK - Steam.wav",
"Lightning": "Dueling/ATK - Lightning.wav",
"Lava": "Dueling/ATK - Lava.wav",
"Fire": "Dueling/ATK - Fire.wav",
"Ice": "Dueling/ATK - Ice.mp3",
"Dust": "Dueling/ATK - Sand.wav",
"Wood": "Dueling/ATK - Wood.wav",
"Light ": "Dueling/ATK - Light .wav",
"Earth": "Dueling/ATK - Earth.wav",
"Water": "Dueling/ATK - Water.mp3",
"Air": "Dueling/ATK - Air.mp3",
}
spellColours = {
"Steam": {"1": "RED", "2": "BLUE", "3": "RED", "4": "BLUE"},
"Lightning": {"1": "RED", "2": "WHITE", "3": "RED", "4": "WHITE"},
"Lava": {"1": "RED", "2": "GREEN", "3": "RED", "4": "GREEN"},
"Fire": {"1": "RED", "2": "RED", "3": "RED", "4": "RED"},
"Ice": {"1": "BLUE", "2": "WHITE", "3": "BLUE", "4": "WHITE"},
"Dust": {"1": "GREEN", "2": "WHITE", "3": "GREEN", "4": "WHITE"},
"Wood": {"1": "GREEN", "2": "BLUE", "3": "GREEN", "4": "BLUE"},
"Light ": {"1": "AMBER", "2": "AMBER", "3": "AMBER", "4": "AMBER"},
"Earth": {"1": "GREEN", "2": "GREEN", "3": "GREEN", "4": "GREEN"},
"Water": {"1": "BLUE", "2": "BLUE", "3": "BLUE", "4": "BLUE"},
"Air": {"1": "WHITE", "2": "WHITE", "3": "WHITE", "4": "WHITE"},
}
## the mixed element spells are supposed to flash between colours i think... i'm just mixing the colours.  sorry.
#  DESIGN : all four seconds except smoke which stops a second early, and the mixed elements which flash between two colours.
#  IMPLEMENTATION : mixed elements get mixed colours.  everything goes 4 seconds, the smoke just lasts for a while.
def stopthathorribleflashing():
#    for i in range(2,50):
#      mydmx.setChannel(i, 0)
#      mydmx.render()

spellDMXcodes = {
#"Fire": {10:0,11:0,15:0,16:0,31:255,32:0,33:0,34:0,35:0,36:0,46:0}
#"Earth": {10:0,11:0,15:0,16:0,31:0,32:255,33:0,34:0,35:0,36:0,46:255}
#"Water": {10:0,11:0,15:0,16:0,31:0,32:0,33:255,34:0,35:0,36:0,46:255}
#"Air": {10:0,11:0,15:0,16:0,31:0,32:0,33:0,34:255,35:0,36:0,46:255}
#"Lava": {10:0,11:0,15:0,16:0,31:255,32:255,33:0,34:0,35:0,36:0,46:255}
#"Steam": {10:0,11:0,15:0,16:0,31:255,32:0,33:255,34:0,35:0,36:0,46:255}
#"Wood": {10:0,11:0,15:0,16:0,31:0,32:255,33:0,34:255,35:0,36:0,46:255}
#"Electricity": {10:0,11:0,15:0,16:0,31:255,32:0,33:255,34:0,35:0,36:0,46:255}
#"Dust": {10:0,11:0,15:0,16:0,31:0,32:255,33:0,34:255,35:0,36:0,46:255}
#"Ice": {10:0,11:0,15:0,16:0,31:0,32:0,33:255,34:255,35:0,36:0,46:255}
#"Light": {10:0,11:0,15:0,16:0,31:0,32:0,33:0,34:0,35:255,36:0,46:255}
#Fire		31	4	46=smoke
#Earth		32	4	46
#Water		33	4	46
#Air		34	4	46
#Lava		31,32	1,1,1,1	46
#Steam		31, 33	1,1,1,1	46
#Wood		32,34	1,1,1,1	46
#Electricity	31,33	1,1,1,1	46
#Dust		32,34	1,1,1,1	46
#Ice		33,34	1,1,1,1	46
#Light		35	4	46
#"10":strobe1
#"11":strobe1
#"15":strobe2
#"16":strobe2
#"31":red
#"32":green
#"33":blue
#"34":white
#"35":amber
#"36":intensity (light is on)
#"46":smoke
}
def smokeyflashy(spellDMXcode):
    # TODO : loop through DMXcode array, set most of the things to zero and a couple to 255
#    for i in range(2,50):
#      mydmx.setChannel(spellDMXcode[i])
#    mydmx.render()    
    # TODO: wait four seconds.  how should we do that?  a callback?
    stopthathorribleflashing()

def ive_been_attacked(payload):
    # TODO: not sure if this sound is supposed to happen straight away, or not until both podiums go
    play(spellSounds[playerStartState['Spell']])
    # TODO: this message may need to be broken up into 2 - depends on where the DMX controlllers live...
    hostmqtt.publishL('dmx', 'dmx', 'play', {
                    "Spell": playerStartState['Spell'],
                    "Parcans": spellColours[playerStartState['Spell']],
                })
    
def reconcile_magic():
    global skip_ABC_reset
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
                skip_ABC_reset = 1
        if their_magic_cast['modifier'] == 'disable':
            playerCurrentState['Attack'] = 0
            playerCurrentState['Boost'] = 0
            playerCurrentState['Counter'] = 0
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
    global health
    if nfcTag == payload['tag']:
        health = 0
        report_state('remove-nfc')
        reset()
    else:
        nfcTag = payload['tag']
        report_state('set-nfc')
        play('Dueling/Magic Detected.mp3')


#	F	    E	    W	    A
#F	Fire	Lava	Steam	Lightning
#E	Lava	Earth	Wood	Dust
#W	Steam	Wood	Water	Ice
#A	Lightning	Dust	Ice	Air
spellTypes = {
    'F': 'Fire',
    'E': 'Earth',
    'W': 'Water',
    'A': 'Air',

    'FE': 'Lava',
    'FW': 'Steam',
    'FA': 'Lightening',

    'EF': 'Lava',
    'EW': 'Wood',
    'EA': 'Dust',

    'WF': 'Steam',
    'WE': 'Wood',
    'WA': 'Ice',

    'AF': 'Lightening',
    'AE': 'Dust',
    'AW': 'Ice',
}

def calculateMagic(magic):
    avg = (magic['Fire'] + magic['Earth'] + magic['Water'] + magic['Air']) / 4
    spell = 'light'
    magic_key = ''
    if magic['Fire'] > avg:
        magic_key += 'F'
    if magic['Earth'] > avg:
        magic_key += 'E'
    if magic['Water'] > avg:
        magic_key += 'W'
    if magic['Air'] > avg:
        magic_key += 'A'
    if magic_key in spellTypes:
        spell = spellTypes[magic_key]
    return spell

# info from the database
def get_magic(topic, payload):
    #{"Earth": 10, 
    # "time": "2018-12-22T20:43:40.715609", 
    # "nfc": "550A5CBC", 
    # "Fire": 10, 2700
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
        playerStartState = {}
        playerStartState['Attack'] = baselineStats['Attack'] * (magic['Fire']*10/100)
        playerStartState['Boost'] = baselineStats['Boost'] * (magic['Earth']*10/100)
        playerStartState['Counter'] = baselineStats['Counter'] * (magic['Air']*10/100)
        playerStartState['Energy'] = baselineStats['Energy'] * (magic['Water']*10/100)
        playerStartState['Spell'] = calculateMagic(magic)
        global playerCurrentState
        playerCurrentState = playerStartState
        # send player's currentState to other podium
        hostmqtt.publishL(otherPodium, DEVICENAME, 'player-state', playerCurrentState)

        global health
        health = 100 * playerCurrentState['Energy'] / playerStartState['Energy']
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
    if payload['tag'] == magic['uhf']:
        hostmqtt.publishL(myHostname, DEVICENAME, 'magic_cast', {
                    'nfc': nfcTag,
                    'magic': magic,
                    'modifier': modifier,
                })
        report_state('uhf-cast-magic')
    else:
        report_state('uhf-wrong-magic-item')

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
touchdevice = 'blackpodium'
if myHostname == 'podium1':
    touchdevice = 'silverpodium'
elif myHostname == 'podium2':
    touchdevice = 'goldpodium'

hostmqtt.subscribeL('+', touchdevice, 'touch', set_modifier)
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