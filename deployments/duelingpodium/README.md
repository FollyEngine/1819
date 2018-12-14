# 2 dualling podiums

2 time each.....

## RPi connected to:

* Long range UHF RFID reader
  * [x] one SPARKFUN with external antenna (works)
  * [ ] one serial reader with big antenna
* [x] powered speaker using PHAT-DAC (works)
* neopixel on rpi proto board to show  (some code)
  * [x] health bar (16 pixels)
* [x] mifare rfid reader (works)
* USB power


## ESP32
* touch sensors - 3 or 4 selectors
* [touch arduino sketch](../src/wemos/wemos_button/wemos_button.ino)
* USB power

## shaker controller
* wemos mini boards with ir control...
* [ir relay arduino sketch](../src/wemos/wemos_ir/wemos_ir.ino)
* USB power


## Microservices:

* Long range UHF reader (one of...)
  * [x] [thinkmagic rfid event source](../../src/RPi/rfid-ThinkMagic/main.py)
  * [ ] [serial rfid event source](../../src/RPi/rfid-serial/main.py)
* [x] [mifare rfid event source](../../src/RPi/rfid-mifare/main.py)
* [x] [audio player sink](../../src/RPi/audio/main.py)
* [x] [neopixel sink](../../src/RPi/neopixels/main.py) (not sure - this may running one per neopixel string with cfg?)
* [ ] [podium controller generated from designer](../../controller/podium/main.py)


## initial testing controller:

1. waits for a user to "login" using their personal mifare tag
2. displays user's health
3. waits for wand/orb/magic item to be registered as cast using the UHF reader
4. plays magic audio - `/usr/share/scratch/Media/Sounds/Effects/Pop.wav`, `./Sounds/Effects/Rattle.wav`, `./Sounds/Human/FingerSnap.wav`, `./Sounds/Vocals/Singer1.wav`, `./Sounds/Animal/Goose.wav`