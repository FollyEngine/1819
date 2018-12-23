import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

state = -1
#GPIO.setup(7,GPIO.OUT)
#GPIO.setup(40,GPIO.OUT)
#GPIO.output(7,0)
#GPIO.output(40,0)

try:
	while True:

		time.sleep(0.3)
		if (GPIO.input(11) == 1):
			if (state != 0):
				print "STATE CHANGE"
			state = 0
			print state

		if (GPIO.input(22) == 1):
			if (state != 1):
				print "STATE CHANGE"
			state = 1
			print state

except KeyboardInterrupt:
	GPIO.cleanup()
