# Arduino IDE setup
## Board is
BN: Unknown board
VID: 1A86
PID: 7523
SN: Upload any sketch to obtain it

## IDE installation
* Download arduino IDe from https://www.arduino.cc/en/Main/Donate (donate five dollars)
* Install the ESP32 module from https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-mac-and-linux-instructions/
* Add yourself to the dialout group `sudo usermod -a -G dialout $USER` (or just edit /etc/group)
..* try endless other things until you can select a port from the tools dropdown
* The boards we have use ESP32 Dev Module

## Compiling wemos_orb
* copy mqtt and dependencies to wemos_orb folder
..* `cp ../esp32village/mqtt/mqtt.h src/wemos/wemos_orb/`
..* `cp ../esp32village/mqtt/mqtt.cpp src/wemos/CapacitiveTouch/`

* From Sketch | Incude Library | Manage ibraries, install 
..* PubSubSclient by Nick O'Leary 2.7.0
..* Adafruit NeoPixel library 1.1.7
* Download arduinojson from https://github.com/bblanchon/ArduinoJson/archive/master.zip then install it with Sketch | Include library | Add zip library

Now wemos_orb should have no dependency errors, just compile errors.
Fix the compile errors, then:

 
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
Fix the compile errors, then:
* 

------------------
FLASH MODE DOUT : 80MHz : 921600
esptool.py v2.3.1
Connecting......
Chip is ESP32D0WDQ6 (revision (unknown 0xa))
Features: WiFi, BT, Dual Core, VRef calibration in efuse
Uploading stub...
Running stub...
Stub running...
Changing baud rate to 921600
Changed.
Configuring flash size...

A fatal error occurred: Invalid head of packet ('\xa6')
A fatal error occurred: Invalid head of packet ('\xa6')

---
DOUT : 40MHz : 921600
same but \xe0
---
QIO : 40MHz : 921600
same
---
DIO : 16Mb  : 921600

Configuring flash size...

A fatal error occurred: Timed out waiting for packet content
A fatal error occurred: Timed out waiting for packet content
---
DIO : 32Mb : 921600 : debug level info

esptool.py v2.3.1
Connecting.....
Chip is ESP32D0WDQ6 (revision (unknown 0xa))
Features: WiFi, BT, Dual Core, VRef calibration in efuse
Uploading stub...
Running stub...
Stub running...
Changing baud rate to 921600
Changed.
Configuring flash size...

A fatal error occurred: Invalid head of packet ('\xc6')
A fatal error occurred: Invalid head of packet ('\xc6')
---
