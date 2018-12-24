#!//usr/bin/python3

import time
import RPi.GPIO as GPIO

import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import mqtt

# mqtt setup
mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, "relay_from")
hostmqtt.loop_start()   # use the background thread

master_mqtt_host = config.getValue("mqttmaster", "mqtt.thegame.folly.site")
mastermqtt = mqtt.MQTT(master_mqtt_host, myHostname, "relay_to", "everyone", "S4C7Tzjc2gD92y9", 1883)


# wire sensor setup
GPIO.setmode(GPIO.BOARD)

GPIO.setup(15,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# TODO : publish notifications to mqtt server

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

## a function that publishes an event to mosquito
## hostmqtt.publishL("all", "audio", "mute", {})
