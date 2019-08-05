

// secrets.h defines SECRET_SSID and SECRET_PASSWORD (and we assume the local network has an accessible mqtt host)
#include "secrets.h"

#include "mqtt.h"

#include <ArduinoJson.h>

char deviceType[] = "motion";

//BUILD with "LOLIN(WEMOS) D1 R2 & mini"
Mqtt mqtt = Mqtt(SECRET_SSID, SECRET_PASSWORD, "mqtt.local", 1883, deviceType);

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

// Looks like the small wemos board PIR shield isn't very good at motion detection (not a huge surprise)

int motionState = LOW;
unsigned long nextStatusMessage = 0;
void loop() {
  mqtt.loop();  // Note - this sends a regular status:listening message - every 5minutes

  // PIR sensor is on pin D3
  int val = digitalRead(D3);
  //Serial.printf("read %d\n", val);
  //low = no motion, high = motion
  if (val != motionState) {
    motionState = val;
    StaticJsonBuffer<200> jsonBuffer;
    JsonObject& root = jsonBuffer.createObject();
    if (motionState == LOW) {
      root["pir"] = "no motion";
    } else {
      root["pir"] = "motion detected";
    }
    mqtt.publish(deviceType, "motion", root);
  }
}
