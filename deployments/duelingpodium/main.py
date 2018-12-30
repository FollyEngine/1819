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
import copy

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

touchdevice = 'blackpodium'
if myHostname == 'podium1':
    touchdevice = 'silverpodium'
elif myHostname == 'podium2':
    touchdevice = 'goldpodium'


########################################
def play(sound):
    hostmqtt.publishL(myHostname, 'audio', 'play', {
                    'sound': sound,
                    #'tagid': payload['tag']
                })
health = 0
def show_health(tip = 'off'):
    hostmqtt.publishL(myHostname, 'neopixel', 'play', {
                    'operation': 'health',
                    'count': health,
                    'colour': 'blue',
                    'tip': tip,
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
"Light": "Dueling/ATK - Light .wav",
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
"Light": {"1": "AMBER", "2": "AMBER", "3": "AMBER", "4": "AMBER"},
"Earth": {"1": "GREEN", "2": "GREEN", "3": "GREEN", "4": "GREEN"},
"Water": {"1": "BLUE", "2": "BLUE", "3": "BLUE", "4": "BLUE"},
"Air": {"1": "WHITE", "2": "WHITE", "3": "WHITE", "4": "WHITE"},
}

def reconcile_magic(t_topic, t_payload):
    if my_magic_cast == None or their_magic_cast == None:
        print('reconcile_magic not ready')
        return

    global skip_ABC_reset
    global playerCurrentState
    global their_magic_cast
    counter_reflected_attack = False
    their_attack_disabled = False
    my_attack_disabled = False
    my_attack_value = playerCurrentState['Attack']
    print('reconcile_magic, I cast: %s, they cast: %s' % (my_magic_cast['modifier'], their_magic_cast['modifier']))
    # we use their cast info to determin the effects on us
    if their_magic_cast['modifier'] == 'attack':
        print('they attack %d' % opponentsCurrent['Attack'])
        if opponentsCurrent['Attack'] == 0:
            their_attack_disabled = True
        elif my_magic_cast['modifier'] == 'counter':
            print('I counter')
            opponentsCurrent['Attack'] = opponentsCurrent['Attack'] - playerCurrentState['Counter']
            print("My counter reduced their attach by %d to %d" % (playerCurrentState['Counter'], opponentsCurrent['Attack']))
            if opponentsCurrent['Attack'] < 0:
                # this means their attack reflects on them (see below)
                counter_reflected_attack = True
                opponentsCurrent['Attack'] = 0
        elif my_magic_cast['modifier'] == 'boost':
            print('i boosted, it failed')
            global boost
            boost = 0
            skip_ABC_reset = 0
        elif my_magic_cast['modifier'] == 'attack':
            print('i attack %d' % playerCurrentState['Attack'])

        if not their_attack_disabled:
            playerCurrentState['Energy'] = playerCurrentState['Energy'] - opponentsCurrent['Attack']
    else:
        if my_magic_cast['modifier'] == 'attack':
            print('I attack %d' % playerCurrentState['Attack'])
            if playerCurrentState['Attack'] == 0:
                my_attack_disabled = True
            elif their_magic_cast['modifier'] == 'counter':
                print('they counter')
                my_attack_value = playerCurrentState['Attack'] - opponentsCurrent['Counter']
                if my_attack_value < 0:
                    print("Their counter (%d) reflected some of my attack: %d" % (opponentsCurrent['Counter'], my_attack_value))
                    # some of my attack energy was reflected onto me
                    counter_reflected_attack = True
                    playerCurrentState['Energy'] = playerCurrentState['Energy'] + my_attack_value
        if my_magic_cast['modifier'] == 'boost':
            print('i boosted')
            #boost attack and counter for next round (or again and again) - again, use the round number
            print("boosting Attack from: %d" % playerCurrentState['Attack'])
            playerCurrentState['Attack'] = playerCurrentState['Attack'] + (playerCurrentState['Attack'] * (playerCurrentState['Boost']/100))
            print("boosting Counter to: %d" % playerCurrentState['Counter'])
            playerCurrentState['Counter'] = playerCurrentState['Counter'] + (playerCurrentState['Counter'] * (playerCurrentState['Boost']/100))
            skip_ABC_reset = 1

    hostmqtt.publishL(myHostname, DEVICENAME, 'health', {'player': playerCurrentState['Energy'], 'opponent_attack': opponentsCurrent['Attack']})
    print("my energy %d, their energy %d" % (playerCurrentState['Energy'], opponentsCurrent['Energy']))

    if their_magic_cast['modifier'] == 'disable':
        print('they cast disable')
        if my_magic_cast['modifier'] == 'attack':
            playerCurrentState['Attack'] = 0
        elif my_magic_cast['modifier'] == 'boost':
            playerCurrentState['Boost'] = 0
        elif my_magic_cast['modifier'] == 'counter':
            playerCurrentState['Counter'] = 0
        skip_ABC_reset = 1


    # FX for this duel
    if counter_reflected_attack:
        # reflected attack
        print("---- countered!")
        if my_magic_cast['modifier'] == 'attack' and not my_attack_disabled:
            spell = calculateMagic(magic)
            print("--- countered my attack(%s) reflected"% spell)
            play(spellSounds[spell])
        if their_magic_cast['modifier'] == 'attack' and not their_attack_disabled:
            spell = calculateMagic(their_magic_cast['magic'])
            print("--- countered their attack(%s) reflected"% spell)
            hostmqtt.publishL('dmx', 'dmx', 'play', {
                'From': myHostname,
                'From2': touchdevice,
                'Spell': spell,
                "Parcans": spellColours[spell],
                "Counter": "Reflected",
                })    
    else:
        # if they attack me
        if their_magic_cast['modifier'] == 'attack' and not their_attack_disabled:
            spell = calculateMagic(their_magic_cast['magic'])
            print("their attack(%s)"% spell)
            play(spellSounds[spell])
        if my_magic_cast['modifier'] == 'attack' and not my_attack_disabled:
            spell = calculateMagic(magic)
            print("my attack(%s)"% spell)
            hostmqtt.publishL('dmx', 'dmx', 'play', {
                'From': myHostname,
                'From2': touchdevice,
                'Spell': spell,
                "Parcans": spellColours[spell],
                })    
    if my_attack_disabled:
        play('Dueling/Disable.wav')
    if my_magic_cast['modifier'] == 'boost':
        play('Dueling/Boost.wav')
    elif my_magic_cast['modifier'] == 'counter' and counter_reflected_attack:
        play('Dueling/Counter.wav')
    elif my_magic_cast['modifier'] == 'disable':
        play('Dueling/Disable.wav')

    # send player's currentState to other podium
    hostmqtt.publishL(otherPodium, DEVICENAME, 'player-state', playerCurrentState)
    report_state('combat!')
    global health
    health = 100 * playerCurrentState['Energy'] / playerStartState['Energy']
    hostmqtt.publishL(myHostname, DEVICENAME, 'health', {'health': health})
    if health <= 0:
        hostmqtt.publish('combat-end', {'I': 'died'})

    reset()
    hostmqtt.publishL(otherPodium, DEVICENAME, 'player-state', playerCurrentState)
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
    spell = 'Light'
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
    new_wand_set = False
    if payload['nfc'] == nfcTag:
        if magic == None or magic['nfc'] != payload['nfc']:
            print('set_magic ------------------- ONCE per combat')
            play('Dueling/Magic Detected.mp3')
            magic = payload
            global playerStartState
            playerStartState = {}

            ########################################
            # Fire: Attack, Earth: Boost%, Air: Counter, Water: Energy
            baselineStats = {'Attack': 10, 'Boost': 100, 'Counter': 15, 'Energy': 40}

            playerStartState['Attack'] = baselineStats['Attack'] * (magic['Fire']*10/100)
            playerStartState['Boost'] = baselineStats['Boost'] * (magic['Earth']*10/100)
            playerStartState['Counter'] = baselineStats['Counter'] * (magic['Air']*10/100)
            playerStartState['Energy'] = baselineStats['Energy'] * (magic['Water']*10/100)
            playerStartState['Spell'] = calculateMagic(magic)
            global playerCurrentState
            playerCurrentState = copy.deepcopy(playerStartState)
            # send player's currentState to other podium
            hostmqtt.publishL(otherPodium, DEVICENAME, 'player-state', playerCurrentState)

            global health
            health = 100 * playerCurrentState['Energy'] / playerStartState['Energy']
            show_health()
            report_state('set-magic-stats')
            new_wand_set = True
    if not new_wand_set:
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
        if their_magic_cast != None:
            # you can only cast once per turn
            return
        # TODO: this needs to be the other podium's playerCurrentState
        their_magic_cast = payload
    else:
        global my_magic_cast
        if my_magic_cast != None:
            # you can only cast once per turn
            return
        my_magic_cast = payload
        show_health('white')

    hostmqtt.publishL(otherPodium, DEVICENAME, 'player-state', playerCurrentState)
    hostmqtt.publishL('all', DEVICENAME, 'reconcile_magic', {'reason': 'magic_was_cast'})

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
def msg_combat_end(topic, payload):
    global health
    if health <= 0:
        hostmqtt.publishL(myHostname, 'neopixel', 'combat-end', {'colour': 'red', 'count': 3})
    else:
        hostmqtt.publishL(myHostname, 'neopixel', 'combat-end', {'colour': 'blue', 'count': 3})
    time.sleep(2)

    health = 0
    reset()

########################################


# Listen for rfid-nfc scan events
# lookup that tag's health, and send it out to that host's neopixel/play
# wait X seconds, and then turn off.. (or listen for removed event?)

# test signal
hostmqtt.subscribeL("all", DEVICENAME, "test", test_msg)

hostmqtt.subscribeL(myHostname, 'rfid-nfc', "scan", read_nfc)
hostmqtt.subscribeL('all', 'db_lookup', 'magic-item', get_magic)

hostmqtt.subscribeL('+', touchdevice, 'touch', set_modifier)
hostmqtt.subscribeL(myHostname, 'yellow-rfid', "scan", read_uhf)
hostmqtt.subscribeL('+', DEVICENAME, "magic_cast", magic_cast)

hostmqtt.subscribeL('+', DEVICENAME, 'reconcile_magic', reconcile_magic)
hostmqtt.subscribeL('+', DEVICENAME, "combat-end", msg_combat_end)

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