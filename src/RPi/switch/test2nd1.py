import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(7,GPIO.OUT)
GPIO.output(7,0)

try:
	while True:
		GPIO.output(7, GPIO.input(11) )

except KeyboardInterrupt:
	GPIO.cleanup()
