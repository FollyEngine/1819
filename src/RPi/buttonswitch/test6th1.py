
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

#from neopixels  import 
#import neopixels
# uses https://github.com/jgarff/rpi_ws281x.git 
# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
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

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

colours = {
    'off': Color(0,0,0),
    'white': Color(180,180,180),
    'green': Color(255,0,0),
    'red': Color(0,255,0),
    'blue': Color(0,0,255),
    'yellow': Color(255,255,0)
}


import RPi.GPIO as GPIO
import time



GPIO.setmode(GPIO.BOARD)

GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

state = -1
interval = 5
standingBy = True

#GPIO.setup(7,GPIO.OUT)
#GPIO.setup(40,GPIO.OUT)
#GPIO.output(7,0)
#GPIO.output(40,0)


print interval, "seconds"

colorWipe(strip,colours['blue'],50)

try:
	while standingBy:
		time.sleep(0.25)


		if (GPIO.input(11) == 1):
			if (state != 0):
				print "STATE CHANGE"
			state = 0
			print state
			colorWipe(strip,colours['green'],50)

			interval = 5
			print interval, " seconds"
			time.sleep(interval)
			
#			while (GPIO.input(11) == 0):
#				while (GPIO.input(22) == 0):
#					colorWipe(strip,colours['green'],50)
#					colorWipe(strip,colours['off'],50)

				
		if (GPIO.input(22) == 1):
			if (state != 1):
				print "STATE CHANGE"
			state = 1
			print state
			colorWipe(strip,colours['red'],50)

			interval = 6
			print interval, " seconds"
			time.sleep(interval)

#			while (GPIO.input(11) == 0):
#				while (GPIO.input(22) == 0):
#					colorWipe(strip,colours['red'],50)
#					colorWipe(strip,colours['off'],50)



		if (state == -1):
			rainbow(strip,20,1)


		if (state == 0):
			colorWipe(strip,colours['green'],50)
			colorWipe(strip,colours['off'],50)

		if (state == 1):
			colorWipe(strip,colours['red'],50)
			colorWipe(strip,colours['off'],50)
			




except KeyboardInterrupt:
	GPIO.cleanup()
