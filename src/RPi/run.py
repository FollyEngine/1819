#!/usr/bin/python3
#
# run.py reads the config.yml, 
# and uses that to decide what services to start

import yaml
import time
import argparse
import logging
import os

# the config and mqtt modules are in a bad place atm :/
import sys
sys.path.append('./mqtt/')
import config
import mqtt
import subprocess

DEVICENAME="deployment"
myHostname = config.getHostname(False)

mqttHost = config.getValue("mqtthostname", "localhost")
for i in range(0, 25):
    time.sleep(1)
    response = os.system("ping -c 1 " + mqttHost)
    if response == 0:
        break
    logging.info("Waiting for %s: attempt %s"% (mqttHost, i))

mqttMasterHost = config.getValue("mqttmaster", "")
if mqttMasterHost != "":
    for i in range(0, 25):
        time.sleep(1)
        response = os.system("ping -c 1 " + mqttMasterHost)
        if response == 0:
            break
        logging.info("Waiting for %s: attempt %s"% (mqttMasterHost, i))

hostmqtt = mqtt.MQTT(mqttHost, myHostname, DEVICENAME)
#hostmqtt.loop_start()   # don't use the background thread (can't publish results from the background?)

########################################
def startServices():
    if myHostname not in hostsConfig:
        logging.log("%s not in hosts config" % (myHostname))
        return
    hostConfig = hostsConfig[myHostname]
    deploymentType = hostConfig["type"]
    deployments = config.getValue("deployments", {})
    for devicename in deployments[deploymentType]:
        t=deployments[deploymentType][devicename]["type"]
        hostmqtt.status({"starting": t})

        cmd = './'+t+'/main.py'
        process = subprocess.Popen(
            ['sudo', cmd, myHostname, deploymentType, devicename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

########################################
# on update git message
def msg_git(topic, payload):
    gitcmd = mqtt.get(payload, 'cmd', 'done')
    if gitcmd == 'done':
        # the reply? - ignore it
        return
    if not gitcmd in ('pull', 'log', 'status'):
        logging.info("git %s not permitted" % gitcmd)
        hostmqtt.publish("git", {
            "ran": gitcmd,
            "result": "error",
            "exception": "not permitted"
        })
        return
    params = ''
    if gitcmd == 'status':
        params = '-sb'
    if gitcmd == 'log':
        params = '--oneline -1'
    logging.info("git %s" % gitcmd)
    try:
        # TODO: send the output back to the mqtt server?
        result = subprocess.check_output(
            "git %s %s" % (gitcmd, params), 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True
            )
        logging.info("git %s\n%s\n" % (gitcmd, result))
        hostmqtt.publish("git", {
            "ran": gitcmd,
            "result": result
        })
        logging.info("git DONE")
    except Exception as ex:
        logging.error("git %s: Exception occurred" % gitcmd, exc_info=True)
        hostmqtt.publish("git", {
            "ran": gitcmd,
            "result": "error",
            "exception": ex
        })

hostmqtt.subscribe("git", msg_git)


########################################
# on update config message
def msg_update_config(topic, payload):
    logging.info("Received config: %s" % (payload))
    global config
    global hostsConfig
    if mqtt.MQTT.topic_matches_sub(hostmqtt, myHostname+"/"+DEVICENAME+"/update_config", topic):
        logging.info("Setting config")
        # TODO: OMG ew!
        config.cfg = mqtt.get(payload, 'config', {})
        hostsConfig = config.getValue("hosts", {})

hostmqtt.subscribe("update_config", msg_update_config)

########################################
hostmqtt.status({"status": "STARTING"})
hostsConfig = config.getValue("hosts", {})
while myHostname not in hostsConfig:
    # request a config from the server
    logging.info("Requesting config")
    hostmqtt.publish("requestconfig", {
        #host type, ip, other things
    })
    time.sleep(5)

logging.info("Starting services")

startServices()

hostmqtt.status({"status": "listening"})

try:
    hostmqtt.loop_forever()
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

hostmqtt.status({"status": "STOPPED"})
