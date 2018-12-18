/*
Using Touch Intrrerupts from wires attached to magical objects
The bigger the threshold, the more sensible is the touch (see int threshold)

when a wire is touched, it emits an mqtt message on mqtt topid esp32-XXXXXXXXXX/XXXXpodium/touch
with json contents like {"touch7":true,"device":"silverpodium","time":"2018-12-17T23:05:13"}

*/

#include "mqtt.h"

// One podium is gold, the other is silver.  uncomment the podium you're updating here
char podiumName[] = "goldpodium";
// char podiumName[] = "silverpodium";

Mqtt mqtt = Mqtt("ASUS", "MEGA SHED", "10.10.11.2", 1883, podiumName);

// BUILD as WEMOS LOLIN32 - see http://esp32village.blogspot.com/2018/04/esp32.html
// OR
// BUILD as "ESP32 Dev Module", using 115200 baud and DOUT Flash mode, see https://github.com/LilyGO/ESP32-MINI-32-V2.0

int threshold = 40;
bool current[8] = {false,false,false,false,false,false,false,false};
bool last[8] = {false,false,false,false,false,false,false,false};
bool touchState[8] = {false,false,false,false,false,false,false,false};

void gotTouch0(){
 current[0] = true;
}
void gotTouch1(){
 current[1] = true;
}
void gotTouch2(){
 current[2] = true;
}
void gotTouch3(){
 current[3] = true;
}
void gotTouch4(){
 current[4] = true;
}
void gotTouch5(){
 current[5] = true;
}
void gotTouch6(){
 current[6] = true;
}
void gotTouch7(){
 current[7] = true;
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
  char name[16];

  mqtt.loop();

  bool stateChange = false;
  for (int i=0; i<8; i++) {
    if (current[i] == last[i] && last[i] != touchState[i]) {
      // need to report this as a state change.
      stateChange = true;
      touchState[i] = current[i];
      Serial.printf("Touch %d detected\n", i);
      snprintf(name, 16, "touch%d", i);
      root[name] = touchState[i];
    }

    // prepare for next loop
    last[i] = current[i];
    current[i] = false;
  }
  if (stateChange) {
      mqtt.publish(podiumName, "touch", root);
  }
  
  
  //Serial.printf("w %d, %d, %d, %d, %d, %d, %d, %d, %d, %d\n", touchRead(T0), touchRead(T1), touchRead(T2), touchRead(T3), touchRead(T4), touchRead(T5), touchRead(T6), touchRead(T7), touchRead(T8), touchRead(T9));  // get value using T0
  delay(50);
}
