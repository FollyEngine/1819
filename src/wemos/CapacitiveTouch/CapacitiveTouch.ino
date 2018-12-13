/*
This is un example howto use Touch Intrrerupts
The bigger the threshold, the more sensible is the touch
*/

#include "mqtt.h"

Mqtt mqtt = Mqtt("ASUS", "MEGA SHED", "192.168.4.1", 1883, "podiumbuttons");

// BUILD as WEMOS LOLIN32 - see http://esp32village.blogspot.com/2018/04/esp32.html
// OR
// BUILD as "ESP32 Dev Module", using 115200 baud and DOUT Flash mode, see https://github.com/LilyGO/ESP32-MINI-32-V2.0

int threshold = 40;
bool touch0detected = false;
bool touch1detected = false;
bool touch2detected = false;
bool touch3detected = false;
bool touch4detected = false;
bool touch5detected = false;
bool touch6detected = false;
bool touch7detected = false;

void gotTouch0(){
 touch0detected = true;
}

void gotTouch1(){
 touch1detected = true;
}

void gotTouch2(){
 touch2detected = true;
}
void gotTouch3(){
 touch4detected = true;
}
void gotTouch4(){
 touch4detected = true;
}
void gotTouch5(){
 touch5detected = true;
}

void gotTouch6(){
 touch6detected = true;
}
void gotTouch7(){
 touch7detected = true;
}

void setup() {
  Serial.begin(115200);
  mqtt.setup();
  delay(1000); // give me time to bring up serial monitor
  
  Serial.println("ESP32 Touch Interrupt Test");
  touchAttachInterrupt(T0, gotTouch0, threshold);
//  touchAttachInterrupt(T1, gotTouch1, threshold); // Attached to the reset button (on the LOLIN32), so won't work as capacitive
  touchAttachInterrupt(T2, gotTouch2, threshold);   // Touch 2 doesn't work on the TTGO ESP32
  touchAttachInterrupt(T3, gotTouch3, threshold);
  touchAttachInterrupt(T4, gotTouch4, threshold);
  touchAttachInterrupt(T5, gotTouch5, threshold);
  touchAttachInterrupt(T6, gotTouch6, threshold);
  touchAttachInterrupt(T7, gotTouch7, threshold);
}

void loop(){
  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();

  mqtt.loop();

  if(touch0detected){
    touch0detected = false;
    Serial.printf("Touch 0 (pin %d) detected\n", T0);
    root["pin"] = 0;
    mqtt.publish("podiumbuttons", "touch", root);
  }
  if(touch1detected){
    touch1detected = false;
    Serial.printf("Touch 1 (pin %d) detected\n", T1);
    root["pin"] = 1;
    mqtt.publish("podiumbuttons", "touch", root);
  }
  if(touch2detected){
    touch2detected = false;
    Serial.printf("Touch 2 (pin %d) detected\n", T2);
    root["pin"] = 2;
    mqtt.publish("podiumbuttons", "touch", root);
  }
  if(touch3detected){
    touch3detected = false;
    Serial.printf("Touch 3 (pin %d) detected\n", T3);
    root["pin"] = 3;
    mqtt.publish("podiumbuttons", "touch", root);
  }
  if(touch4detected){
    touch4detected = false;
    Serial.printf("Touch 4 (pin %d) detected\n", T4);
    root["pin"] = 4;
    mqtt.publish("podiumbuttons", "touch", root);
  }
  if(touch5detected){
    touch5detected = false;
    Serial.printf("Touch 5 (pin %d) detected\n", T5);
    root["pin"] = 5;
    mqtt.publish("podiumbuttons", "touch", root);
  }
  if(touch6detected){
    touch6detected = false;
    Serial.printf("Touch 6 (pin %d) detected\n", T6);
    root["pin"] = 6;
    mqtt.publish("podiumbuttons", "touch", root);
  }
  if(touch7detected){
    touch7detected = false;
    Serial.printf("Touch 7 (pin %d) detected\n", T7);
    root["pin"] = 7;
    mqtt.publish("podiumbuttons", "touch", root);
  }
  
  
  Serial.printf("w %d, %d, %d, %d, %d, %d, %d, %d, %d, %d\n", touchRead(T0), touchRead(T1), touchRead(T2), touchRead(T3), touchRead(T4), touchRead(T5), touchRead(T6), touchRead(T7), touchRead(T8), touchRead(T9));  // get value using T0
  delay(1000);
}
