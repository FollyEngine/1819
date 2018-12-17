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

DEVICENAME="healthpixels"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

# uses https://github.com/jgarff/rpi_ws281x
# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
# when _not_ using the pHAT DAC, you can use all sorts of pins :)
# GPIO13, GPIO18, GPIO21, and GPIO19
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
if LED_PIN in {13, 19, 41, 45, 53}:
    LED_CHANNEL = 1

# Bizzareness when using 4 separate neopixel arrays:
# solder to GPIOs 12, 18, 19, 21: the driving 12 or 18 lights up both arrays both times, and 13, which is not connected also drives one
# solder to GPIOs 13, 18, 19, 21: driving 19 will light up 2 of the arrays, but driving 13, 18, 21 and 12 gets the 4 different arrays


# Create NeoPixel object with appropriate configuration.
strips = {}
#strips["up"] = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strips["up"] = Adafruit_NeoPixel(LED_COUNT, 13, LED_FREQ_HZ, 1, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strips["down"] = Adafruit_NeoPixel(LED_COUNT, 18, LED_FREQ_HZ, 0, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strips["left"] = Adafruit_NeoPixel(LED_COUNT, 19, LED_FREQ_HZ, 1, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strips["right"] = Adafruit_NeoPixel(LED_COUNT, 21, LED_FREQ_HZ, 0, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strips["up"].begin()
strips["down"].begin()
strips["left"].begin()
strips["right"].begin()

# can do things like:
#  mosquitto_pub -h mqtt -t two/DEVICENAME/play -m '{"operation": "theatrechase", "colour": "green"}'

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

def health(strip, color, count, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    if count > strip.numPixels():
        count = strip.numPixels()
    for i in range(count):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def magic_item(strip, payload):
    wait_ms = 0
    index = 0
    total = payload['A'] + payload['B'] + payload['C'] + payload['D']
    A = int(round(payload['A'] * strip.numPixels() / total))
    B = int(round(payload['B'] * strip.numPixels() / total))
    C = int(round(payload['C'] * strip.numPixels() / total))
    D = int(round(payload['D'] * strip.numPixels() / total))
    print("A: %d, B: %d, C: %d, D: %d" % (A, B, C, D))
    for i in range(A):
        strip.setPixelColor(index, colours['red'])
        index = index + 1
        strip.show()
        time.sleep(wait_ms/1000.0)
    for i in range(B):
        strip.setPixelColor(index, colours['green'])
        index = index + 1
        strip.show()
        time.sleep(wait_ms/1000.0)
    for i in range(C):
        strip.setPixelColor(index, colours['blue'])
        index = index + 1
        strip.show()
        time.sleep(wait_ms/1000.0)
    for i in range(D):
        strip.setPixelColor(index, colours['yellow'])
        index = index + 1
        strip.show()
        time.sleep(wait_ms/1000.0)

############
operations = {
    # custom = has A, B, C, D
    'magic_item': magic_item,
    # needs colour and count
    'health': health,
    #needs colour
    'colourwipe': colorWipe,
    'theatrechase': theaterChase,
    #no colour option
    'rainbow': rainbow,
    'rainbow_cycle': rainbowCycle,
}
colours = {
    'off': Color(0,0,0),
    'white': Color(180,180,180),
    'green': Color(255,0,0),
    'red': Color(0,255,0),
    'blue': Color(0,0,255),
    'yellow': Color(255,255,0)
}
############
def get(obj, name, default):
    result = default
    if name in obj:
        result = obj[name]
    return result


def play(payload = {}):
    direction = get(payload, 'direction', 'up')
    strip = get(strips, direction, strips['up'])

    operationname = get(payload, 'operation', 'colourwipe')
    operation = get(operations, operationname, operations['colourwipe'])
    print("playing %s" % operationname)

    if operationname == 'magic_item':
        operation(strip, payload)
        return

    if operationname == 'rainbow' or operationname == 'rainbow_cycle':
        operation(strip)
        return

    colourname = get(payload, 'colour', 'off')
    colour = get(colours, colourname, colours['off'])
    # TODO: maybe change to using HTML colours #000000 style?
    if operationname == 'colourwipe' or operationname == 'theatrechase':
        operation(strip, colour)
        return

    count = get(payload, 'count', 16)
    operation(strip, colour, count)

########################################
# on_message subscription functions
def msg_play(topic, payload):
    if mqtt.MQTT.topic_matches_sub(hostmqtt, "all/"+DEVICENAME+"/play", topic):
        # everyone
        #print("everyone plays "+payload)
        play(payload)
    elif mqtt.MQTT.topic_matches_sub(hostmqtt, myHostname+"/"+DEVICENAME+"/play", topic):
        #print(myHostname+" got "+payload+" SPARKLES!!")
        play(payload)

def msg_test(topic, payload):
    play({'operation': 'colourwipe', 'colour': 'yellow'})


hostmqtt.subscribe("play", msg_play)
hostmqtt.subscribeL("all", DEVICENAME, "play", msg_play)
hostmqtt.subscribeL("all", DEVICENAME, "test", msg_test)

hostmqtt.status({"status": "listening"})
play({'operation': 'colourwipe', 'colour': 'red', 'direction': 'up'})
play({'operation': 'colourwipe', 'colour': 'off', 'direction': 'up'})

play({'operation': 'colourwipe', 'colour': 'green', 'direction': 'left', 'count': 5})
play({'operation': 'colourwipe', 'colour': 'off', 'direction': 'left'})

play({'operation': 'colourwipe', 'colour': 'blue', 'direction': 'down', 'count': 10})
play({'operation': 'colourwipe', 'colour': 'off', 'direction': 'down'})

play({'operation': 'colourwipe', 'colour': 'white', 'direction': 'right'})
play({'operation': 'colourwipe', 'colour': 'off', 'direction': 'right'})

try:
    while True:
        time.sleep(1)
except Exception as ex:
    traceback.print_exc()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})
