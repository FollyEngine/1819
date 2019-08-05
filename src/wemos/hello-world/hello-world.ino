

// secrets.h defines SECRET_SSID and SECRET_PASSWORD (and we assume the local network has an accessible mqtt host)
#include "secrets.h"

#include "mqtt.h"

#include <ArduinoJson.h>

char deviceType[] = "hello";

// Listen to mqtt messages and change LEDs in response.  Test with a message like
// mosquitto_pub -h "mqtt" -t "all/orbX/twinkle" -m "twinkle"
// GO READ https://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/

//BUILD with "LOLIN(WEMOS) D1 R2 & mini"
Mqtt mqtt = Mqtt(SECRET_SSID, SECRET_PASSWORD, "mqtt.local", 1883, deviceType);
// Mqtt mqtt = Mqtt("uhome", "WhatTheHe11", "mqtt.local", 1883, deviceType);

void mqtt_callback_fn(const char* topic, byte* payload, unsigned int length) {
  Serial.printf("Callback: %s\n", topic);
}

void setup() {
  //while (!Serial);
  Serial.begin(115200);
  Serial.printf("Started\n");

  mqtt.setCallback(mqtt_callback_fn);
  mqtt.setup();
}


unsigned long nextStatusMessage = 0;
void loop() {
  if (nextStatusMessage < millis()) {
    sendStatus();
    nextStatusMessage = millis() + (30*1000); // wait 30 seconds
  }
}

void sendStatus() {
  // Using ArduinoJson 5
  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  mqtt.loop();

  root["info"] = "Something";
  mqtt.publish(deviceType, "status", root);
}
