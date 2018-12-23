import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)


GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


try:
	while True:
		if (GPIO.input(11) == 1):
			print "GPIO 11 is 1"
	#	else 
	#		print "GPIO 11 is not 1"


except KeyboardInterrupt:
	GPIO.cleanup()
