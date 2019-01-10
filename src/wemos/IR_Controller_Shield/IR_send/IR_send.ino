/* IRremoteESP8266: IRsendDemo - demonstrates sending IR codes with IRsend.
 *
 * Version 1.0 April, 2017
 * Based on Ken Shirriff's IrsendDemo Version 0.1 July, 2009,
 * Copyright 2009 Ken Shirriff, http://arcfn.com
 *
 *  
 The Woodford Game 1819.  wobbleboard controller for the magic podium
 use board LOLIN (WEMOS) D1 R2 & Mini
 The IR detector (kRecvPin) is on D4


 
POWER button
Encoding  : NEC
Code      : FF807F (32 bits)

PLAY button
Encoding  : NEC
Code      : FF20DF (32 bits)

PAUSE
Encoding  : NEC
Code      : FF00FF (32 bits)

big P
Encoding  : NEC
Code      : FF609F (32 bits)

WALK
Encoding  : NEC
Code      : FF906F (32 bits)

RUN
Encoding  : NEC
Code      : FF08F7 (32 bits)

SPRINT
Encoding  : NEC
Code      : FF8877 (32 bits)


 *
 * An IR LED circuit *MUST* be connected to the ESP8266 on a pin
 * as specified by kIrLed below.
 */

#ifndef UNIT_TEST
#include <Arduino.h>
#endif

// messaging stuff
#include <ArduinoJson.h>
#include "mqtt.h"
// Listen to mqtt messages and send an IR signal in response.  Test with a message like
// mosquitto_pub -h "mqtt" -t "all/wobbleboard/wobble" -m "wobble"
Mqtt mqtt = Mqtt("ASUS", "MEGA SHED", "mqtt.local", 1883, "wobbleboard");
char* button = "";
char* lastbutton = "";
uint64_t signal = 0x00000000UL;  // set initial IR signal to nothing
boolean initialised = false;

// IR stuff
#include <IRremoteESP8266.h>
#include <IRsend.h>


const uint16_t kIrLed = 0;  // ESP8266 GPIO pin to use. Recommended: 4 (D2).

IRsend irsend(kIrLed);  // Set the GPIO to be used to sending the message.

void mqtt_callback_fn(const char* topic, byte* payload, unsigned int length) {
  StaticJsonBuffer<200> jsonBuffer;
  Serial.printf("Callback: %s\n", topic);
  Serial.println();
  Serial.printf("payload: %s\n", payload);
  Serial.println();
  // we've received a message.  send an IR message to the wobbleboard
  JsonObject& jsonpayload=jsonBuffer.parseObject((char*)payload);
  if (!jsonpayload.success()){
    Serial.println("could not decode that payload");
  }
  const char* buttonstatus = jsonpayload["status"];
  Serial.printf("buttonstatus: %s\n\n", buttonstatus);

  if (buttonstatus=="POWER") {
    signal=0x00FF807F;
    button="POWER";
  }
}

void setup() {
  Serial.begin(115200, SERIAL_8N1, SERIAL_TX_ONLY);

  // messaging stuff
  mqtt.setCallback(mqtt_callback_fn);
  mqtt.setup();

  // IR stuff
  irsend.begin();

  // TODO: do something quick to the wobbleboard so we know it's working
  Serial.println("Turning the wobbleboard of/on with 2 seconds in between");
  irsend.sendNEC(0x00FF807FUL, 32);  // press the power button every two seconds
  delay(2000);
  irsend.sendNEC(0x00FF807FUL, 32);  // press the power button every two seconds
  
}

void loop() {  
  // messaging stuff
  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  mqtt.loop();
  // this doesn't work in setup()
  if (!initialised) {
    delay(1);
//    initialised = mqtt.subscribe(mqtt.getHostname(), "wobbleboard", "button");  // gethostname doesn't work
    initialised = mqtt.subscribe("all", "wobbleboard", "button");
    Serial.printf("mqtt Subscription returned: %s\n", initialised ? "true" : "false");
  }
  root["status"]=button;
  mqtt.publish("wobbleboard", "status", root);

  // IR stuff
  delay(2000);
  Serial.println("POWER toggle");
  irsend.sendNEC(0x00FF807F, 32);  // press the power button every two seconds
/*  this works
  delay(2000);
  Serial.println("NEC PLAY");
  irsend.sendNEC(0x00FF20DF, 32);  // press the power button every two seconds
*/

  lastbutton = button;
}
