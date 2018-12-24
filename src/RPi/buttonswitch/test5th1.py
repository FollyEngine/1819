


import RPi.GPIO as GPIO
import time



GPIO.setmode(GPIO.BOARD)

GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

state = -1
interval = 4
standingBy = True

#GPIO.setup(7,GPIO.OUT)
#GPIO.setup(40,GPIO.OUT)
#GPIO.output(7,0)
#GPIO.output(40,0)

interval = 4
print interval, "seconds"

try:
	while standingBy:
		
		time.sleep(0.5)
		
		if (GPIO.input(11) == 1):
			if (state != 0):
				print "STATE CHANGE"
			state = 0
			print state

			interval = 5
			print interval, " seconds"
			time.sleep(interval)
			
		if (GPIO.input(22) == 1):
			if (state != 1):
				print "STATE CHANGE"
			state = 1
			print state

			interval = 6
			print interval, " seconds"
			time.sleep(interval)
		


except KeyboardInterrupt:
	GPIO.cleanup()
