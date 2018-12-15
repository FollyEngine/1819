#!//usr/bin/python

import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import sys
import socket
import traceback


allMuted = False
repeats = {}


# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import mqtt
import config
import datetime

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, "ThingMagic")
hostmqtt.loop_start()

# see https://github.com/gotthardp/python-mercuryapi
import mercury

# end load config

########################################
lastRead = {}
def rfidTagDataCallback(rfid):
    try:
        if rfid.epc.hex() in lastRead:
            if datetime.timedelta.total_seconds(datetime.datetime.now()-lastRead[rfid.epc.hex()]) < (1):
                #lets only report each tag once a second
                return

        lastRead[rfid.epc.hex()] = datetime.datetime.now()
        event = {
            'atr': rfid.epc_mem_data,
            'tag': rfid.epc.hex(),
            'rssi': rfid.rssi,
            'event': 'inserted'
        }
        hostmqtt.publish("scan", event)

        print("EPC: %s RSSI: %s\n" % (rfid.epc, rfid.rssi))
        #print("     epc_mem_data: %s" % rfid.epc_mem_data)
        #print("     tid_mem_data: %s" % rfid.tid_mem_data)
        #print("     user_mem_data: %s" % rfid.user_mem_data)
        #print("     reserved_mem_data: %s" % rfid.reserved_mem_data)
    except Exception as ex:
        traceback.print_exc()


########################################
def status():
    hostmqtt.status({
        "model": reader.get_model(),
        "region": "AU",
        #"temp": reader.get_temperature(),
        "power_range": reader.get_power_range(),
        "antennas": reader.get_antennas(),
#        "power": reader.get_read_powers(),
        "status": "listening"})

########################################

reader = mercury.Reader("tmr:///dev/ttyACM0")

reader.set_region("AU")
reader.set_read_plan([1], "GEN2")
reader.set_read_powers([1], [2700])

#using this causes the python to hang
#reader.set_read_plan([1], "GEN2", bank=["reserved"], read_power=2700)

lastStatus = datetime.datetime.now()
status()
reader.start_reading(rfidTagDataCallback, on_time=100, off_time=0)


while True:
    if datetime.timedelta.total_seconds(datetime.datetime.now()-lastStatus) > (2*60):
        status()
        lastStatus = datetime.datetime.now()
    try:
        time.sleep(1)
        print(".")
        #print(reader.read())
    except KeyboardInterrupt:
        print("exit")
        break
    except Exception as ex:
        traceback.print_exc()


reader.stop_reading()

hostmqtt.status({"status": "STOPPED"})
