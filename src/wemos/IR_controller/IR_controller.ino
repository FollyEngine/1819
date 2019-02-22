/* IRremoteESP8266: IRsendDemo - demonstrates sending IR codes with IRsend.
 *
 * Version 1.0 April, 2017
 * Based on Ken Shirriff's IrsendDemo Version 0.1 July, 2009,
 * Copyright 2009 Ken Shirriff, http://arcfn.com
 *
 *  
 The Woodford Game 1819.  wobbleboard controller for the magic podium
 By Andrew Lorien (almost nothing left from Ken)
 use board LOLIN (WEMOS) D1 R2 & Mini
 The IR detector (kRecvPin) is on D4

NOTES :
The statuses you can pass are based on the graphics on the remote buttons:
"POWER","PLAY","PAUSE","BIG P","WALK","RUN","SPRINT"
mosquitto_pub -h "mqtt" -t "all/wobbleboard/wobble" -m '{"status":"PAUSE","device":"thegame","time":"2018-12-22T06:17:40"}'

Don't use "POWER" because it is a toggle switch with no feedback, no way of knowing whether the power is off or on
On the factory remote:
  You must press "PLAY" before you can press "WALK", "RUN", or "SPRINT"
  You must press "PAUSE" to stop, and the board slows gradually.  
  When you press "PLAY" again the board starts at the slowest speed
In this program:
  When you send "WALK", "RUN", or "SPRINT" we send a "PLAY" signal first
  - so the only statuses you need are "WALK", "RUN", "SPRINT", "PAUSE"

The LOLIN device should be 
- directly above the board
- up to three metres away, but that reduces to one if it's at an angle
- facing in any direction (there are 4 IR lights on the device).
- in direct line of sight.
The PAUSE command is most sensitive, other commands work twice as far away.
The board beeps whenever you send a signal.  there is no volume control


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
// mosquitto_pub -h "mqtt" -t "all/wobbleboard/wobble" -m '{"status":"PAUSE","device":"thegame","time":"2018-12-22T06:17:40"}'

Mqtt mqtt = Mqtt("ASUS", "MEGA SHED", "mqtt.local", 1883, "wobbleboard");

uint64_t signal = 0x00000000;  // set initial IR signal to nothing
boolean initialised = false;

// IR stuff
#include <IRremoteESP8266.h>
#include <IRsend.h>
const uint16_t kIrLed = 0;  // ESP8266 GPIO pin to use. Recommended: 4 (D2).
IRsend irsend(kIrLed);  // Set the GPIO to be used to sending the message.

void mqtt_callback_fn(const char* topic, byte* payload, unsigned int length) {
  StaticJsonBuffer<200> jsonBuffer;
  Serial.println();
  Serial.printf("Callback: %s\n", topic);
  Serial.printf("payload: %s\n", payload);

  // we've received a message.  convert it to an IR code
  JsonObject& jsonpayload=jsonBuffer.parseObject((char*)payload);
  if (!jsonpayload.success()){
    Serial.println("could not decode that payload");
  }
  const char* button = jsonpayload["status"];
  Serial.printf("button: %s\n\n", button);
  // if the signal is "WALK", "RUN", or "SPRINT" we press play first
  if (( strcmp("WALK",button) == 0 )||( strcmp("RUN",button) == 0 )||( strcmp("SPRINT",button) == 0 )) {
    irsend.sendNEC(buttonsignal("PLAY"), 32);  
  }
  
  signal=buttonsignal(button);

  if (signal != 0x00000000){
    Serial.printf("%11x" PRIx64, signal);  // for ff807f prints ff807fllx ?
    irsend.sendNEC(signal, 32);  
    signal = 0x00000000;  
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
  Serial.println("Turning the wobbleboard off/on with 2 seconds in between (it should beep twice)");
  irsend.sendNEC(0x00FF807FUL, 32);  // press the power button 
  delay(2000);
  irsend.sendNEC(0x00FF807FUL, 32);  // press the power button again
  
}

void loop() {  
  // messaging stuff
  mqtt.loop();
  // this doesn't work in setup()
  if (!initialised) {
    delay(1);
//    initialised = mqtt.subscribe(mqtt.getHostname(), "wobbleboard", "button");  // gethostname doesn't work
    initialised = mqtt.subscribe("all", "wobbleboard", "button");
    Serial.printf("mqtt Subscription returned: %s\n", initialised ? "true" : "false");
  }

}
uint16_t buttonsignals[] = { 0x00FF807F,0x00FF20DF,0x00FF00FF,0x00FF609F,0x00FF906F,0x00FF08F7,0x00FF8877 };
const char* buttonnames[] = { "POWER","PLAY","PAUSE","BIG P","WALK","RUN","SPRINT" };

uint16_t buttonsignal(const char* button){
  for (int i = 0;  i<7; i++){
    if ( strcmp(buttonnames[i],button) == 0 ){
      return buttonsignals[i];
    }
  }
  return 0x00000000;
}
/*
POWER button
Code      : FF807F (32 bits)

PLAY button
Code      : FF20DF (32 bits)

PAUSE
Code      : FF00FF (32 bits)

big P
Code      : FF609F (32 bits)

WALK
Code      : FF906F (32 bits)

RUN
Code      : FF08F7 (32 bits)

SPRINT
Code      : FF8877 (32 bits)

 */
