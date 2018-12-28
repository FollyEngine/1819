#!//usr/bin/python3
# This is the DMX server which controls both sets of effects
# - two strobes, one PAR can, one smoke machine, one pin spot
# all that times two

import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
from time import sleep

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import mqtt
import config

import pysimpledmx
import time

# this is ugly but times are tough
try:
  mydmx = pysimpledmx.DMXConnection("/dev/ttyUSB0")
except:
    print("DMX failed on USB0")  
    try:
      mydmx = pysimpledmx.DMXConnection("/dev/ttyUSB1")
    except:
	print("DMX failed on USB1")  
	try:
	  mydmx = pysimpledmx.DMXConnection("/dev/ttyUSB2")
	except:
	    print("DMX failed on USB2")  
	    try:
	      mydmx = pysimpledmx.DMXConnection("/dev/ttyUSB3")
	    except:
		print("DMX failed on USB3")  
		try:
		  mydmx = pysimpledmx.DMXConnection("/dev/ttyUSB4")
		except:
		    print("DMX failed on USB4")  

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, "relay_from")
hostmqtt.loop_start()   # use the background thread

master_mqtt_host = config.getValue("mqttmaster", "mqtt.thegame.folly.site")
mastermqtt = mqtt.MQTT(master_mqtt_host, myHostname, "relay_to", "everyone", "S4C7Tzjc2gD92y9", 1883)



def stopthathorribleflashing():
    print("stoppit")
    for i in range(2,50):
      mydmx.setChannel(i, 0)
#     print(i)

def smokeyflashy(DMXadjustment, spellDMXcode):
    print("smokeyflashy")
    # TODO : loop through DMXcode array, set most of the things to zero and a couple to 255
    thisDMX = spellDMXcodes[spellDMXcode]
    print(thisDMX)
    for dmx in thisDMX:
      print(dmx+DMXadjustment)
      mydmx.setChannel(dmx+DMXadjustment, 255)      
      
    # TODO: wait four seconds.  how should we do that?  a callback?
    time.sleep(4)
    stopthathorribleflashing()

def attack(topic, payload):
    try:
      mastermqtt.status({"status": "attacked!"})
      print("attacked!")
      # decode the json, it should look like this, where the podium is the one sending the spell
  #podium2/dmx/play {'from': 'podium2', 'spell':'Air'}
  #podium1/dmx/play {'from': 'podium1', 'spell':'Electricity'}
      DMXadjustment = 0
      if payload["from"] == "poduim2":
	DMXadjustment = 100
      
      smokeyflashy(DMXadjustment, payload["spell"])
    except Exception as ex:
        traceback.print_exc()

# these codes are for one side.  the other side is just the same +100
spellDMXcodes = {
"Fire": [37,31,46],
"Earth": [37,32,46],
"Water": [37,33,46],
"Air": [37,34,46],
"Lava": [37,31,32,46],
"Steam": [37,31,33,46],
"Wood": [37,32,34,46],
"Electricity": [37,31,33,46],
"Dust": [37,32,34,46],
"Ice": [37,33,34,46],
"Light": [37,35,46],
"Strobe": [11,12]
}
smokeyflashy(0,"Electricity")

stopthathorribleflashing()

mastermqtt.subscribeL("+", "dmx", "play", attack)

hostmqtt.status({"status": "listening"})
mastermqtt.status({"status": "listening"})

try:
    #while True:
    #    sleep(1)
    mastermqtt.loop_forever()
except Exception as ex:
    traceback.print_exc()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})
mastermqtt.status({"status": "STOPPED"})
