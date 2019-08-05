#include "mqtt.h"

#include <ArduinoJson.h>

#include <Adafruit_NeoPixel.h>

char orbName[] = "neopixel1";



breif:
change all pixels to a specified colour
length of transition from one colour to another
and make it twinkle for a length of time (using the specified colour as the background

// Listen to mqtt messages and change LEDs in response.  Test with a message like
// mosquitto_pub -h "mqtt" -t "all/orbX/twinkle" -m "twinkle"
// mosquitto_pub -t "all/neopixel1/twinkle" -m "twinkle"
// GO READ https://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/

//BUILD with "LOLIN(WEMOS) D1 R2 & mini"
//Mqtt mqtt = Mqtt("ASUS", "MEGA SHED", "mqtt.local", 1883, orbName);
 Mqtt mqtt = Mqtt("Folly", "Fight the Dull, you fools!", "10.10.11.150", 1883, orbName);

// constants won't change. They're used here to set pin numbers:
// D3 is the LOLIN Wemos 1-Button Shield: https://wiki.wemos.cc/products:d1_mini_shields:1-button_shield
const int ledPin =  1;      // the number of the LED pin

// D4 is the default pin for the 6 LED RBG shield
// https://wiki.wemos.cc/products:d1_mini_shields:rgb_led_shield
// https://github.com/wemos/D1_mini_Examples/blob/master/examples/04.Shields/RGB_LED_Shield/simple/simple.ino
//#define PIN   D4

// When we setup the NeoPixel library, we tell it how many pixels, and which pin to use to send signals.
// Note that for older NeoPixel strips you might need to change the third parameter--see the strandtest
// example for more information on possible values.
#define LED_NUM 50
Adafruit_NeoPixel left_leds = Adafruit_NeoPixel(LED_NUM, D5, NEO_GRB + NEO_KHZ800);

boolean on = false;
boolean changed = false;
void mqtt_callback_fn(const char* topic, byte* payload, unsigned int length) {
  Serial.printf("Callback: %s\n", topic);
  // we've received a message.  reset the LEDs as appropriate
  changed=true;
  // if topic=twinkle set ON
  if (true) {
    on = true; 
  } 
  // if topic=stop unset ON
  if (false) {
    on = false; 
  } 


}

// TODO: set brightness and colour set from mqtt payload
#define BRIGHTNESS 140   // 140 is reasonably bright
boolean initialised = false;
int colour = 0;

void setup() {
  //while (!Serial);
  Serial.begin(115200);
  Serial.printf("Started\n");


  // initialize the LED pin as an output:
  pinMode(ledPin, OUTPUT);
  pinMode(ledPin, LOW);
  
  left_leds.begin(); // This initializes the NeoPixel library.
  left_leds.setBrightness(BRIGHTNESS);
  left_leds.show();                // turn on all pixels
  
  mqtt.setCallback(mqtt_callback_fn);
  mqtt.setup();

}

// this function sets all the pixels in a group to the same colour
void leds_set(Adafruit_NeoPixel &leds, uint8 R, uint8 G, uint8 B) {
  for(uint16_t i=0; i<LED_NUM; i++) {
    leds.setPixelColor(i, R, G, B);    
    leds.show();
    //delay(50);
  }
}



// from https://learn.adafruit.com/sparkle-skirt/code-battery
// Here is where you can put in your favorite colors that will appear!
// just add new {nnn, nnn, nnn}, lines.
uint8_t myFavoriteColors[][3] = {
       {255,   222,  30},   // Pixie GOLD
       {50, 255, 255},    // Alchemy BLUE
       {255, 100, 0},     // Animal Orange 
       {242,    90, 255},   // Garden PINK
       {0,    255, 40},   // Tinker GREEN
     };
// don't edit the line below
#define FAVCOLORS sizeof(myFavoriteColors) / 3
int dim = 20;
int moredim = 50;

void loop() {
// IDEA : should the orb do a tiny twinkle every few minutes just to let us know it's alive?  
  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  mqtt.loop();

  if (!initialised) {
    //leds_set(left_leds, 0, 0, 0);
    // turn off the cpu board led
    digitalWrite(ledPin, HIGH);
  
    delay(1);
    initialised = mqtt.subscribe(mqtt.getHostname(), orbName, "twinkle");
    initialised = mqtt.subscribe("all", orbName, "twinkle");
    Serial.printf("loop Subscription returned: %s\n", initialised ? "true" : "false");
    // esp8266-84f3eb3b74a6/button/pushed
    for (int i = 0; i < 2*LED_NUM; i++) {
      pixie_dust(left_leds, colour);
      delay(1);
    }
  }
  if (changed) {
    if (on) {
      // rotate colours, turn LEDs on but dim
      root["orbstatus"]="twinkling";
      mqtt.publish(orbName, "status", root);
      pinMode(ledPin, HIGH);
    
      colour++;
      if (colour > FAVCOLORS) {
        colour = 0;
      }
  
      // turn LEDs on to the current colour
      uint8 red = myFavoriteColors[colour][0];
      uint8 green = myFavoriteColors[colour][1];
      uint8 blue = myFavoriteColors[colour][2]; 
      leds_set(left_leds, red/moredim, green/moredim, blue/moredim);
    }
    if (!on) {
      // turn leds off and go back to waiting state
      root["orbstatus"]="not twinkling";
      mqtt.publish(orbName, "status", root);
  
      pinMode(ledPin, LOW);
  
      leds_set(left_leds, 0,0,0);
    }
    changed = false;    
  }
  if (on) {
    // sparkle each led once (but in random order, so some of them might sparkle twice and some not at all)      
// TODO actually just choose a random LED and sparkle it, since this loop now repeats every time
    for (int i = 0; i < LED_NUM; i++) {
      pixie_dust(left_leds, colour);
      delay(2);
    }
  }
}


// from https://learn.adafruit.com/neopixel-pixie-dust-bag/arduino-code
    #define DELAY_MILLIS 10  // how long each light stays bright for, smaller numbers are faster 
    #define DELAY_MULT 8     // Randomization multiplier on the delay speed of the effect
     
    bool oldState = HIGH; //sets the initial variable for counting touch sensor button pushes
     
    void pixie_dust(Adafruit_NeoPixel &leds, int showColor) {
      //color (0-255) values to be set by cycling touch switch, initially GOLD
      uint8 red = myFavoriteColors[colour][0];
      uint8 green = myFavoriteColors[colour][1];
      uint8 blue = myFavoriteColors[colour][2]; 
                
      //sparkling
      int p = random(LED_NUM); //select a random pixel
      leds.setPixelColor(p,red,green,blue); //color value comes from cycling state of momentary switch
      leds.show();
      delay(DELAY_MILLIS * random(DELAY_MULT) ); //delay value randomized to up to DELAY_MULT times longer
      leds.setPixelColor(p, red/dim, green/dim, blue/dim); //set to a dimmed version of the state color
      leds.show();
      leds.setPixelColor(p+1, red/moredim, green/moredim, blue/moredim); //set a neighbor pixel to an even dimmer value
      leds.show();
      
//      //button check to cycle through color value sets
//      bool newState = digitalRead(TOUCH_PIN); //Get the current button state
//      // Check if state changed from high to low (button press).
//      if (newState == LOW && oldState == HIGH) {
//        // Short delay to debounce button.
//        delay(20);
//        // Check if button is still low after debounce.
//        newState = digitalRead(TOUCH_PIN);
//        if (newState == LOW) {
//          showColor++;
//          if (showColor > 4)
//            showColor=0;
//           }   
//      }
      // Set the last button state to the old state.
//      oldState = newState;  
      
    }




// Fadeout... starts at bright white and fades to almost zero
void fadeout(Adafruit_NeoPixel &leds) {  
  // swap these two loops to spin around the LEDs
  for(uint16_t fade=255; fade>0; fade=fade-17) {
      for(uint16_t i=0; i<LED_NUM; i++) {
        // now we will 'fade' it in steps
          
          leds.setPixelColor(i, leds.Color(fade,fade,fade));
      } 
      leds.show();
      delay(5); // milliseconds
  }
  // now make sure they're all set to 0
  for(uint16_t i=0; i<LED_NUM; i++) {
    leds.setPixelColor(i, leds.Color(0,0,0));
  }
  leds.show();

}


// first number is 'wait' delay, shorter num == shorter twinkle
// second number is how many neopixels to simultaneously light up
// THIS FUNCTION IS NOT USED AND PROBABLY DOESN'T WORK
void flashRandom(Adafruit_NeoPixel &leds, int wait, uint8_t howmany) {
 
  for(uint16_t i=0; i<howmany; i++) {
    // pick a random favorite color!
    int c = random(FAVCOLORS);
    int red = myFavoriteColors[c][0];
    int green = myFavoriteColors[c][1];
    int blue = myFavoriteColors[c][2]; 
 
    // get a random pixel from the list
    int j = random(leds.numPixels());
    //Serial.print("Lighting up "); Serial.println(j); 
    
    // now we will 'fade' it in 5 steps
    for (int x=0; x < 5; x++) {
      int r = red * (x+1); r /= 5;
      int g = green * (x+1); g /= 5;
      int b = blue * (x+1); b /= 5;
      
      leds.setPixelColor(j, leds.Color(r, g, b));
      leds.show();
      delay(wait);
    }
    // & fade out in 5 steps
    for (int x=5; x >= 0; x--) {
      int r = red * x; r /= 5;
      int g = green * x; g /= 5;
      int b = blue * x; b /= 5;
      
      leds.setPixelColor(j, leds.Color(r, g, b));
      leds.show();
      delay(wait);
    }
  }
  // LEDs will be off when done (they are faded to 0)
}
