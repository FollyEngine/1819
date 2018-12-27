#!//usr/bin/python3
# This is the DMX server which controls both sets of effects
# - two strobes, one PAR can, one smoke machine, one pin spot
# all that times two

import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
from time import sleep

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import mqtt
import config

mqttHost = config.getValue("mqtthostname", "mqtt.local")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, "relay_from")
hostmqtt.loop_start()   # use the background thread

master_mqtt_host = config.getValue("mqttmaster", "mqtt.thegame.folly.site")
mastermqtt = mqtt.MQTT(master_mqtt_host, myHostname, "relay_to", "everyone", "S4C7Tzjc2gD92y9", 1883)

hostmqtt.subscribeL("+", "+", "+", attack)


def stopthathorribleflashing():
    print("stoppit")
#    for i in range(2,50):
#     print(i)

def smokeyflashy(spellDMXcode):
    print("smokeyflashy")
    # TODO : loop through DMXcode array, set most of the things to zero and a couple to 255
    thisDMX=spellDMXcodes[spellDMXcode]
    print(thisDMX)
    for dmx in thisDMX:
      print(dmx)
      
    # TODO: wait four seconds.  how should we do that?  a callback?
    time.sleep(4)
    stopthathorribleflashing()

def attack()
    # mqtt "attack" signal should include the name of the podium being attacked, and the spell 
    mastermqtt.status({"status": "attacked!"})
    
# these codes are for one side.  the other side is just the same +100
spellDMXcodes = {
"Fire": [31,46],
"Earth": [32,46],
"Water": [33,46],
"Air": [34,46],
"Lava": [31,32,46],
"Steam": [31,33,46],
"Wood": [32,34,46],
"Electricity": [31,33,46],
"Dust": [32,34,46],
"Ice": [33,34,46],
"Light": [35,46]
}
smokeyflashy("Electricity")

stopthathorribleflashing()
