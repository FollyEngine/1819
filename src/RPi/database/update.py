#!/usr/bin/python3
# This script adds wands/orbs/ingredients/whatever to the database.
# run it when you need to add new things

# first we need a setup.sh with 
# sudo pip install --no-cache-dir -r ./requirements.txt

# This belongs to the MQTT server, so it's called from src/mqtt which is the parent folder of this file

from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model
import json
import datetime
import logging

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt
from database import *

DEVICENAME="db_update"

mqttHost = config.getValue("mqtthostname", "mqtt.local")
import socket    #TODO: extract!
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)

# update.py is for updating the database
# if you scan an nfc tag, and then a uhf tag, those 2 tags will be put in the MagicItem table
# if either tof those 2 tags is already there, then that row will be updated

# if you scan a UHF tag only, then the ingredients table will have that tag update_or_created.

currentNFC = ""
currentUHF = ""
def scan_nfc(topic, payload):
    global currentNFC
    global currentUHF
    if currentNFC == "":
        currentNFC = payload['tag']
    else:
        if currentNFC == payload['tag'] and \
                currentUHF != "":
            logging.info("SET: nfc = %s, uhf = %s" % (currentNFC, currentUHF))
            item, create = MagicItem.get_or_create(nfc=currentNFC, uhf=currentUHF)
            item.uhc = currentUHF
            item.save()
            i = model_to_dict(item)
            logging.info("Foo: %s" % i)
            hostmqtt.publishL('all', DEVICENAME, 'magic-item', i)
        else:
            logging.info("ERROR: different nfc tag '%s', '%s'" % (currentNFC, payload['tag']))
        currentNFC = ""
        currentUHF = ""

def scan_uhf(topic, payload):
    global currentNFC
    global currentUHF
    if currentUHF == "":
        currentUHF = payload['tag']
        if currentNFC == "":
            logging.info("UHF: %s" % currentUHF)
            magicitem = None
            try:
                magicitem = MagicItem.get(uhf=currentUHF)
            except:
                logging.info("ok")
            if magicitem != None:
                logging.info("UHF %s is a magic item" % currentUHF)
                IngredientItem.delete().where(IngredientItem.uhf == currentUHF).execute()
                currentUHF = ""
                return
            # try:
            #     item = IngredientItem.create(uhf=currentUHF)
            # except:
            #     item = IngredientItem.get(uhf=currentUHF)
            item, create = IngredientItem.get_or_create(uhf=currentUHF)
            i = model_to_dict(item)
            logging.info("Foo: %s" % i)
            hostmqtt.publishL('all', DEVICENAME, 'ingredient-item', i)
    else:
        currentUHF = ""


database_init()
hostmqtt.subscribeL('+', 'rfid-nfc', "scan", scan_nfc)
hostmqtt.subscribeL('+', 'yellow-rfid', "scan", scan_uhf)

hostmqtt.status({"status": "listening"})

try:
    hostmqtt.loop_forever()
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

hostmqtt.status({"status": "STOPPED"})