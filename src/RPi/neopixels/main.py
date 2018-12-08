#!/usr/bin/python

import time
import sys
import socket
#from subprocess import call
import yaml
import time
from neopixel import *
import argparse

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt

DEVICENAME="neopixel"

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)


# uses https://github.com/jgarff/rpi_ws281x.git 
# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 21      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()


# Define functions which animate LEDs in various ways.

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)
############
operations = {
    #needs colour
    'colourwipe': colorWipe,
    'theatrechase': theaterChase,
    #no colour option
    'rainbow': rainbow,
    'rainbow_cycle': rainbowCycle,
}
colours = {
    'off': Color(0,0,0),
    'red': Color(255,0,0),
    'green': Color(0,255,0),
    'blue': Color(0,0,255)
}
############
def get(obj, name, default):
    result = default
    if name in obj:
        result = obj[name]
    return result


def play(payload = {}):
    operationname = get(payload, 'operation', 'colourwipe')
    operation = get(operations, operationname, operations['colourwipe'])
    print("playing %s" % operationname)
    if operationname == 'rainbow' or operationname == 'rainbow_cycle':
        operation(strip)
        return

    colourname = get(payload, 'colour', 'off')
    colour = get(colours, colourname, colours['off'])
    operation(strip, colour)


########################################
# on_message subscription functions
def msg_play(topic, payload):
    if mqtt.MQTT.topic_matches_sub(hostmqtt, "all/neopixel/play", topic):
        # everyone
        #print("everyone plays "+payload)
        play(payload)
    elif mqtt.MQTT.topic_matches_sub(hostmqtt, myHostname+"/neopixel/play", topic):
        #print(myHostname+" got "+payload+" SPARKLES!!")
        play(payload)

hostmqtt.subscribe("play", msg_play)
hostmqtt.subscribeL("all", DEVICENAME, "play", msg_play)

hostmqtt.status({"status": "listening"})
play()

try:
    hostmqtt.loop_forever()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})