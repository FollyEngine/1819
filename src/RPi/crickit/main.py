#!/usr/bin/python3

import time
import sys
import socket
#from subprocess import call
import yaml
import time
#from neopixel import *
from adafruit_crickit import crickit
#from adafruit_seesaw.neopixel import NeoPixel
import argparse
import logging

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt
sys.path.append('./crickit/')
import myneopixels


myHostname = config.getHostname()
deploymenttype=config.getDeploymentType()
DEVICENAME=config.getDevicename()

mqttHost = config.getValue("mqtthostname", "localhost")
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

hostsConfig = config.getValue("hosts", {})
deployments = config.getValue("deployments", {})

logging.info(deployments)

settings = deployments[deploymenttype][DEVICENAME]

logging.info(settings)

# TODO: should get default from DEVICE type, and then over-ride from host settings
#num_pixels = 64  # Number of pixels driven from Crickit NeoPixel terminal
#pixels = NeoPixel(crickit.seesaw, 20, num_pixels)
pixels = myneopixels.MyNeoPixels(64)
pixels.fill(myneopixels.colors['off'])

# can do things like:
#  mosquitto_pub -h mqtt -t two/neopixel/play -m '{"operation": "theatrechase", "colour": "green"}'

############

########################################
# neopixel play
def msg_play(topic, payload):
    if mqtt.MQTT.topic_matches_sub(hostmqtt, "all/"+DEVICENAME+"/play", topic):
        # everyone
        #logging.info("everyone plays "+payload)
        pixels.play(payload)
    elif mqtt.MQTT.topic_matches_sub(hostmqtt, myHostname+"/"+DEVICENAME+"/play", topic):
        #logging.info(myHostname+" got "+payload+" SPARKLES!!")
        pixels.play(payload)

def msg_test(topic, payload):
    pixels.play({'operation': 'colourwipe', 'colour': 'yellow'})

def msg_combat_end(topic, payload):
    colourname = myneopixels.get(payload, 'colour', 'yellow')
    count = myneopixels.get(payload, 'count', 1)
    for i in range(0, count):
        pixels.play({'operation': 'colourwipe', 'colour': colourname})
        pixels.play({'operation': 'colourwipe', 'colour': 'off'})


hostmqtt.subscribe("play", msg_play)
hostmqtt.subscribeL("all", DEVICENAME, "play", msg_play)
hostmqtt.subscribeL("all", DEVICENAME, "test", msg_test)

hostmqtt.subscribeL(myHostname, DEVICENAME, "combat-end", msg_combat_end)

hostmqtt.status({"status": "listening"})
msg_combat_end('one/two/three', {'colour': 'red', 'count': 1})
#hostmqtt.publish('combat-end', {'colour': 'yellow', 'count': 1})

################################################
## servos (can be continuous or positional)
# {
#     throttle: -1.0 to 1.0,
#     angle: 0 to 180,
#     stop: true or false (ignores the other settings)
# }
def msg_servo(topic, payload):
    #if mqtt.MQTT.topic_matches_sub(hostmqtt, "all/"+DEVICENAME+"/servo", topic):
    stop = myneopixels.get(payload, 'stop', False)
    if stop:
        crickit.servo_1._pwm_out.duty_cycle = 0
        return
    continuous_throttle = myneopixels.get(payload, 'throttle', 999)
    if continuous_throttle != 999:
        if continuous_throttle == 0:
            crickit.servo_1._pwm_out.duty_cycle = 0
        else:
            crickit.continuous_servo_1.throttle = continuous_throttle

    angle = myneopixels.get(payload, 'angle', 999)
    if angle != 999:
        crickit.servo_1.angle = angle

hostmqtt.subscribe("servo", msg_servo)


################################################
## touch sensors
touch = (
    crickit.touch_1.raw_value,
    crickit.touch_2.raw_value,
    crickit.touch_3.raw_value,
    crickit.touch_4.raw_value,
)

try:
    while True:
        newtouch = (
            crickit.touch_1.raw_value,
            crickit.touch_2.raw_value,
            crickit.touch_3.raw_value,
            crickit.touch_4.raw_value,
        )
        if abs(newtouch[0]-touch[0]) > 160:
            hostmqtt.publish('touch1', {'value': newtouch[0], 'raw': newtouch[0]})
        if abs(newtouch[1]-touch[1]) > 160:
            hostmqtt.publish('touch2', {'value': newtouch[1], 'raw': newtouch[1]})
        if abs(newtouch[2]-touch[2]) > 160:
            hostmqtt.publish('touch3', {'value': newtouch[2], 'raw': newtouch[2]})
        if abs(newtouch[3]-touch[3]) > 160:
            hostmqtt.publish('touch4', {'value': newtouch[3], 'raw': newtouch[3]})
        touch = newtouch

        time.sleep(0.01)
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

pixels.fill(myneopixels.colors['off'])
hostmqtt.status({"status": "STOPPED"})
