#!/usr/bin/python3

import time
import sys
import socket
#from subprocess import call
import yaml
import time
import argparse

import RPi.GPIO as GPIO


# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt


DEVICENAME="switch"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

# can do things like:
#  mosquitto_pub -h mqtt -t two/DEVICENAME/play -m '{"operation": "theatrechase", "colour": "green"}'

############
def get(obj, name, default):
    result = default
    if name in obj:
        result = obj[name]
    return result

##############

hostmqtt.status({"status": "listening"})

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

state = -1
try:
    while True:
        time.sleep(0.3)
        if (GPIO.input(11) == 1):
            if (state != 0):
                #print("STATE CHANGE")
                hostmqtt.publish("state", {"state": 0})
            state = 0

        if (GPIO.input(22) == 1):
            if (state != 1):
                #print("STATE CHANGE")
                hostmqtt.publish("state", {"state": 1})
            state = 1

        print("State:", state)
except Exception as ex:
    traceback.print_exc()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})
