#!//usr/bin/python
# python3 crashes randomly - python2 worked for the entire convicts run

from __future__ import print_function
from time import sleep

import sys

import smartcard.System

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import CardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException
from smartcard.CardConnection import CardConnection

from threading import Event

# start pcscd daemon
from subprocess import call

import json
import socket


# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt

GETUID = [0xFF, 0xCA, 0x00, 0x00, 0x00]

mqttHost = config.getValue("mqtthostname", "mqtt")
myHostname = config.getValue("hostname", socket.gethostname())
hostmqtt = mqtt.MQTT(mqttHost, myHostname, "rfid-nfc")

# a simple card observer that prints inserted/removed cards
class PrintObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            info = toHexString(card.atr).replace(' ','')
            print("+Inserted: ", info)
            

            connection = card.createConnection()
            connection.connect( CardConnection.T1_protocol )
            response, sw1, sw2 = connection.transmit(GETUID)
            print ('response: ', response, ' status words: ', "%x %x" % (sw1, sw2))
            tagid = toHexString(response).replace(' ','')
            print ("tagid ",tagid)

            hostmqtt.publish("scan", {
                    'atr': info,
                    'tag': tagid,
                    'event': 'inserted'
                })

        for card in removedcards:
            info = toHexString(card.atr).replace(' ','')
            print("+Removed: ", info)
            hostmqtt.publish("removed", {"atr": info, 'event': 'removed'})


###########################################
if __name__ == '__main__':
    call(['/usr/sbin/pcscd'])
    # TODO: detect if there isn't a reader pluigged in, and exit...
    readers = smartcard.System.readers()
    sleep(1)
    if len(readers) < 1:
        print("No RFID readers found, EXITING")
        exit()

    print(readers)

    print("Waiting for smartcard or RFID.")
    print("")
    cardmonitor = CardMonitor()
    cardobserver = PrintObserver()
    cardmonitor.addObserver(cardobserver)

# TODO: use the mqtt retain flag for status messages
    devices=[]
    for r in readers:
        devices.append("%s" % r)
    hostmqtt.status({"status": "listening", "devices": devices})
    cardtype = AnyCardType()

    while True:
        cardrequest = CardRequest(timeout=10, cardType=cardtype)
        try:
            cardservice = cardrequest.waitforcard()
            # stop the loop from spinning the cpu when the rfid tag is left on the reader
            # this stops pcscd from maxing out too
            sleep(1)
        except CardRequestTimeoutException:
            print("retry:")
            sleep(1)
           
        except KeyboardInterrupt:
            print("exit")
            break

    hostmqtt.status({"status": "STOPPED"})

    # don't forget to remove observer, or the
    # monitor will poll forever...
    cardmonitor.deleteObserver(cardobserver)

    import sys
    if 'win32' == sys.platform:
        print('press Enter to continue')
        sys.stdin.read(1)
