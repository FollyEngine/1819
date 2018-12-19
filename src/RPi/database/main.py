#!/usr/bin/python3

from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model
import json
import datetime

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt
sys.path.append('./database/')
from database import *

DEVICENAME="db_lookup"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
import socket    #TODO: extract!
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

# update.py is for updating the database
# if you scan an nfc tag, and then a uhf tag, those 2 tags will be put in the MagicItem table
# if either tof those 2 tags is already there, then that row will be updated

# if you scan a UHF tag only, then the ingredients table will have that tag update_or_created.

def scan_nfc(topic, payload):
    item = MagicItem.get(nfc=payload['tag'])
    i = model_to_dict(item)
    print("Foo: %s" % i)
    hostmqtt.publishL('all', DEVICENAME, 'magic-item', i)

def scan_uhf(topic, payload):
    try:
        magicitem = MagicItem.get(uhf=payload['tag'])
        i = model_to_dict(item)
        print("Foo: %s" % i)
        hostmqtt.publishL('all', DEVICENAME, 'magic-item', i)
        return
    except:
        print("not a magic item")
    try:
        item = IngredientItem.get(uhf=payload['tag'])
        i = model_to_dict(item)
        print("Foo: %s" % i)
        hostmqtt.publishL('all', DEVICENAME, 'ingredient-item', i)
        return
    except:
        print("not an ingredient item")

database_init()
hostmqtt.subscribeL('+', 'rfid-nfc', "scan", scan_nfc)
hostmqtt.subscribeL('+', 'yellow-rfid', "scan", scan_uhf)

hostmqtt.status({"status": "listening"})

try:
    hostmqtt.loop_forever()
except Exception as ex:
    traceback.print_exc()
except KeyboardInterrupt:
    print("exit")

hostmqtt.status({"status": "STOPPED"})