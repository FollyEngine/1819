#!/usr/bin/python

import time
import sys
import socket
import time
import logging
import socket

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt

myHostname = config.getHostname()
deploymenttype=config.getDeploymentType()
DEVICENAME=config.getDevicename()

mqttHost = config.getValue("mqtthostname", "localhost")
hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
hostmqtt.loop_start()   # use the background thread

hostsConfig = config.getValue("hosts", {})
deployments = config.getValue("deployments", {})

logging.info(deployments)

settings = deployments[deploymenttype][DEVICENAME]

logging.info(settings)

############
def get(obj, name, default):
    result = default
    if name in obj:
        result = obj[name]
    return result

########################################
# on_message subscription functions
def msg_play(topic, payload):
    global STATUS
    if mqtt.MQTT.topic_matches_sub(hostmqtt, myHostname+"/"+DEVICENAME+"/reply", topic):
        STATUS = get(payload, 'status', 'red')


STATUS="red"
hostmqtt.subscribe("reply", msg_play)
hostmqtt.status({"status": "listening"})

try:
    while True:
        STATUS="red"

        # get IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            address = s.getsockname()[0]
        except:
            address = "unknown"
        finally:
            s.close()

        hostmqtt.publishL("node-red", "status", "ping", {
            "ping": "hello",
            "from": myHostname,
            "ip": address,
        })
        time.sleep(1)
        hostmqtt.publishL(myHostname, "neopixel-status", "play", {
            "operation": "set",
            "count": 1,
            "colour": STATUS,
        })
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

hostmqtt.status({"status": "STOPPED"})
