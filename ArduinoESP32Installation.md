# Arduino IDE setup

## IDE installation
* Download arduino IDe from https://www.arduino.cc/en/Main/Donate (donate five dollars)
* Install the ESP32 module from https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-mac-and-linux-instructions/
* Add yourself to the dialout group `sudo usermod -a -G dialout $USER` (or just edit /etc/group)

## Compiling wemos_orb
* copy mqtt and dependencies to wemos_orb folder
..* `cp ../esp32village/mqtt/mqtt.h src/wemos/wemos_orb/`
..* `cp ../esp32village/mqtt/mqtt.cpp src/wemos/CapacitiveTouch/`

* From Sketch | Incude Library | Manage ibraries, install 
..* PubSubSclient by Nick O'Leary 2.7.0
..* Adafruit NeoPixel library 1.1.7
* Download arduinojson from https://github.com/bblanchon/ArduinoJson/archive/master.zip then install it with Sketch | Include library | Add zip library

Now wemos_orb should have no dependency errors, just compile errors.
Fix the compile errors, then upload

### Board is
VID: 1A86
PID: 7523
https://tronixlabs.com.au/arduino/boards/wireless/wemos-lolin-d1-mini-arduino-compatible-esp8266-wifi-australia/
* Start Arduino and open Preferences window.
* Enter http://arduino.esp8266.com/stable/package_esp8266com_index.json into Additional Board Manager URLs field. You can add multiple URLs, separating them with commas.
* Open Boards Manager from Tools > Board menu and install esp8266 platform (and don't forget to select your ESP8266 board from Tools > Board menu after installation).  The latest beta didn't support linux so i installed the latest stable, 2.4.2

As it says in the code comments, BUILD with "LOLIN(WEMOS) D1 R2 & mini"



------------------------------------------------------------

## Compiling CapacitiveTouch
* copy mqtt.h to wemos_orb folder
..* `cp ../esp32village/mqtt/mqtt.h src/wemos/CapacitiveTouch/`
..* `cp ../esp32village/mqtt/mqtt.cpp src/wemos/CapacitiveTouch/`
* From Sketch | Incude Library | Manage ibraries, install 
..* PubSubSclient by Nick O'Leary 2.7.0
..* Time by Michael Margolis
..* NTPCLientLib by German Martin
* Download arduinojson from https://github.com/bblanchon/ArduinoJson/archive/master.zip then install it with Sketch | Include library | Add zip library

 
Now CapacitiveTouch should have no dependency errors, just compile errors.
Fix the compile errors, then upload

### Board is
BN: Unknown board
VID: 1A86
PID: 7523
* The boards we have use ESP32 Dev Module.  Add to preferences https://dl.espressif.com/dl/package_esp32_index.json
As it says in the comments at the top of CapacitiveTouch, BUILD as "ESP32 Dev Module", using 115200 baud and DOUT Flash mode, see https://github.com/LilyGO/ESP32-MINI-32-V2.0
* 

------------------------------------------------------------
## Podium sensors

mosquitto_sub -h mqtt -t + -t +/podiumbuttons/+ -v 

|| battle amulet     |function | touch number ||
| flower             | boost   | touch0       |
| diamond stone      | attack  | touch7       |
| brass shell        | counter | touch5       |
| multifaceted stone | debuff  | touch3       |
| black wire         |   -     | touch6       |

if you touch on or off two things at the same time the json includes both in the same report looks like 
{"touch6":true,"touch7":true","device"....}

