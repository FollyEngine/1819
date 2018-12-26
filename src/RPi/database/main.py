#!/usr/bin/python3
# This script should run whileever the mmmporium is open.
# it listens to mqtt messages from scanners (probably cauldron and podium??) and does something databasey about them and publishes a message about that.

# This belongs to the MQTT server, so it's called from src/mqtt which is the parent folder of this file

from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model
import json
import datetime
# this is the main database updater.  it listens for 
# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./')
import config
import mqtt
from database import *

DEVICENAME="db_lookup"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
import socket    #TODO: extract!
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

# update.py is for updating the database

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