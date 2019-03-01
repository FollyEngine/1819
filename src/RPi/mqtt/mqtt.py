

import paho.mqtt.client as mqttclient
import datetime
import json
import logging

class MQTT:
    def __init__(self, mqtthostname, myhostname, devicename, username="", password="", port=1883, transport="tcp"):
        self.mqtthostname = mqtthostname
        self.port = port
        self.transport = transport
        self.myhostname = myhostname
        self.devicename = devicename
        self.username = username
        self.password = password
        self.background_loop = False
        self.sub = {}
        self.connect()

    def status(self, obj):
        obj['device'] = self.devicename
        obj['time'] = datetime.datetime.now().isoformat()
        mqinfo = self.client.publish("%s/%s/%s" % (self.myhostname, self.devicename, 'status'), payload=json.dumps(obj), retain=True)
        if self.background_loop:
            mqinfo.wait_for_publish()

    # used to publish messages to other devices directly, or to `all`
    def publishL(self, host, device, verb, obj):
        obj['device'] = self.devicename
        obj['time'] = datetime.datetime.now().isoformat()
        self.publishStringRaw(host, device, verb, json.dumps(obj))

    def publish(self, verb, obj):
        obj['device'] = self.devicename
        obj['time'] = datetime.datetime.now().isoformat()
        self.publishStringRaw(self.myhostname, self.devicename, verb, json.dumps(obj))

    # used to relay a message from one mqtt broker to another
    # so don't overwrite device and time...
    def relay(self, verb, obj):
        retain = False
        if self.topic_matches_sub("+/+/status", verb):
            logging.debug("Retain: %s" % verb)
            retain = True
        mqinfo = self.client.publish(verb, json.dumps(obj), retain=retain)
        if self.background_loop:
            mqinfo.wait_for_publish()

    def subscribeL(self, host, device, verb, function=""):
        sub_topic = "%s/%s/%s" % (host, device, verb)
        self.client.subscribe(sub_topic)
        logging.info("Subscribed to %s" % sub_topic)
        self.sub[sub_topic] = function

    def subscribe(self, verb, function=""):
        self.subscribeL(self.myhostname, self.devicename, verb, function)


    ############################## internal
    def publishStringRaw(self, host, device, verb, message):
        mqinfo = self.client.publish("%s/%s/%s" % (host, device, verb), message)
        if self.background_loop:
            mqinfo.wait_for_publish()

    def connect(self):
        #TODO: can we ask what clients are connected and detect collisions?
        clientname="%s_%s" % (self.myhostname, self.devicename)
        self.client = mqttclient.Client(client_id=clientname, transport=self.transport)
        if self.username != "":
            self.client.username_pw_set(self.username, self.password)
        #client.on_message=on_message #attach function to callback
        self.client.on_disconnect = self.on_disconnect
        self.client.on_connect = self.on_connect
        self.set_on_message(self.on_message)
        logging.info("Connecting to MQTT as %s at: %s" % (clientname, self.mqtthostname))
        self.client.connect(self.mqtthostname, self.port)

    def set_on_message(self, on_message):
        self.client.on_message=on_message #attach function to callback

    def loop_forever(self):
        self.client.loop_forever()

    def loop_start(self):
        self.client.loop_start()
        self.background_loop = True


    def topic_matches_sub(self, sub, topic):
        return mqttclient.topic_matches_sub(sub, topic)

    def decode(self, raw):
        return json.loads(raw)

    def on_connect(self, client, userdata, flags, rc):
        logging.debug("Connection returned result: ")  #+self.client.connack_string(rc))

    #TODO: this happens when a message failed to be sent - need to resend it..
    def on_disconnect(self, innerclient, userdata,rc=0):
        logging.debug("DisConnected result code "+str(rc))
        self.client.reconnect()
        obj =  {"status": "reconnecting"}
        mqinfo = self.client.publish("%s/%s/%s" % (self.myhostname, self.devicename, 'status'), payload=json.dumps(obj), retain=True)
        if self.background_loop:
            mqinfo.wait_for_publish()

#class Object(object):
#    pass
#a = Object()
#a.topic = "Podium5/audio/play"
#a.payload = '{"sound": "'+testsound+'"}'
#hostmqtt.on_message(mqtt.client, '', a)
    def on_message(self, client, userdata, message):
        message_func = ""
        try:
            logging.debug("on_message %s" % message.topic)
            #logging.debug("message received %s" % payload)
            #logging.debug("message topic=%s" % message.topic)
            #logging.debug("message qos=%s"%message.qos)
            #logging.debug("message retain flag=",message.retain)
            if message.topic in self.sub:
                message_func = self.sub[message.topic]
                logging.debug("direct")
            else:
                for t in self.sub:
                    logging.debug("topic_matches_sub(%s, %s)" % (t, message.topic))
                    if self.topic_matches_sub(t, message.topic):
                        message_func = self.sub[t]
                        logging.debug("match")
                        break

            logging.debug(message_func)
            if message_func == "":
                logging.error("No message_func found for %s" % message.topic)
                return

            raw_payload=str(message.payload.decode("utf-8"))
            logging.debug("HHRAW: "+message.topic+": "+raw_payload)

            if raw_payload == "" or raw_payload == "REMOVED" or raw_payload == "(null)":
                return

            payload = self.decode(raw_payload)
            logging.debug("DECODED: "+message.topic+": "+str(payload))
            message_func(message.topic, payload)
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)
