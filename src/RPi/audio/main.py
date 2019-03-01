#!/usr/bin/python3

import time
import sys
import socket
import pygame
import logging

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt

myHostname = config.getHostname()
deploymenttype=config.getDeploymentType()
DEVICENAME=config.getDevicename()

mqttHost = config.getValue("mqtthostname", "localhost")
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
#hostmqtt.loop_start()   # use the background thread

sounddir = config.getValue("sounddir", "../../sounds/")
testsound = config.getValue("testsound", "test.wav")

# TODO: fix this...
# 100% CPU load using pygame:
# https://github.com/pygame/pygame/issues/331
pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

isMuted = False

############
def play(audiofile):
    if isMuted:
        logging.info(myHostname+" is muted, not playing "+audiofile)
        return
    # if we're already playing something then ignore new play command
    if pygame.mixer.music.get_busy():
        logging.info("audio mixer is busy")
        return

    audioPath = audiofile
    if not audioPath.startswith('/'):
        audioPath = sounddir + audioPath

    # TODO: if its a URL, download it (unless we already have it)

    try:
        pygame.mixer.music.load(audioPath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        hostmqtt.publish("played", {"status": "played", "sound": audiofile})
        logging.info("played %s" % audioPath)
    except Exception as e:
        logging.info("Failed to play %s" % audioPath)
        logging.error("Exception occurred", exc_info=True)

########################################
# on_message subscription functions
def msg_play(topic, payload):
    sound = payload["sound"]
    logging.info("everyone plays "+sound)
    play(sound)

hostmqtt.subscribe("play", msg_play)
hostmqtt.subscribeL("all", DEVICENAME, "play", msg_play)


def msg_test(topic, payload):
    logging.info("everyone plays test.wav")
    play(testsound)

hostmqtt.subscribe("test", msg_test)
hostmqtt.subscribeL("all", DEVICENAME, "test", msg_test)


def msg_mute(topic, payload):
    global isMuted
    isMuted = True
    logging.info("muted")
    pygame.mixer.fadeout(100)

hostmqtt.subscribe("mute", msg_mute)
hostmqtt.subscribeL("all", DEVICENAME, "mute", msg_mute)

def msg_unmute(topic, payload):
    global isMuted
    isMuted = False
    logging.info("unmuted")

hostmqtt.subscribe("unmute", msg_unmute)
hostmqtt.subscribeL("all", DEVICENAME, "unmute", msg_unmute)
########################################

hostmqtt.status({"status": "listening"})

# trigger a play...
play(testsound)

try:
    #while True:
    #    time.sleep(1)
    hostmqtt.loop_forever()
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

hostmqtt.status({"status": "STOPPED"})
