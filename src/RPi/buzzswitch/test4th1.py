import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(15,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

state = -1

aTouched = False
bTouched = False
cTouched = False

#GPIO.setup(7,GPIO.OUT)
#GPIO.output(7,0)


try:
	while True:

#		GPIO.output(7, GPIO.input(11) )
		time.sleep(0.02)			
		if (GPIO.input(11) == 1):
		
			print "A"
			
			if (state == -1):
				print "STATE CHANGE"
				state = 0
			if not bTouched:
				if cTouched:
					print "STATE CHANGE"
					state = 0
			
			aTouched = True	
			bTouched = False
			cTouched = False
			
			print state
			
		elif (GPIO.input(13) == 1):

			bTouched = True

			print "B"
			print state
			
		elif (GPIO.input (15) == 1):

			print "C"

			if (state == -1):
				print "STATE CHANGE"
				state = 1			

			if not bTouched:
				if aTouched:
					print "STATE CHANGE"
					state = 1

			aTouched = False
			bTouched = False
			cTouched = True
			print state
			
			
		else:
#			GPIO.output(7,0)
			print "NO TOUCHING"

			print state

except KeyboardInterrupt:
	GPIO.cleanup()
