# 2 dualling podiums

2 time each.....

## RPi connected to:

* Long range UHF RFID reader
  * one SPARKFUN with external antenna (works)
  * one serial reader with big antenna
* powered speaker using PHAT-DAC (works)
* neopixel on rpi proto board to show  (some code)
  * 4xspell strength bars (16 pixels) - this may move to an esp32/esp8266
  * health bar (16 pixels)
* mifare rfid reader (works)
* USB power


## ESP32
* touch sensors - 3 or 4 selectors
* neopixels for lighting the buttons
* [touch arduino sketch](../src/wemos/wemos_button/wemos_button.ino)
* USB power

## shaker controller
* i'm not sure - I think I have 2 esp8266 ir controller boards
* [ir relay arduino sketch](../src/wemos/wemos_ir/wemos_ir.ino)
* USB power


## Microservices:

* Long range UHF reader (one of...)
  * [thinkmagic rfid event source](../../src/RPi/rfid-ThinkMagic/main.py)
  * [serial rfid event source](../../src/RPi/rfid-serial/main.py)
* [mifare rfid event source](../../src/RPi/rfid-mifare/main.py)
* [audio player sink](../../src/RPi/audio/main.py)
* [neopixel sink](../../src/RPi/neopixels/main.py) (not sure - this may running one per neopixel string with cfg?)
* [podium controller generated from designer](../../controller/podium/main.py)


## initial testing controller:

1. waits for a user to "login" using their personal mifare tag
2. displays user's health
3. waits for wand/orb/magic item to be registered as cast using the UHF reader
4. plays magic audio - `/usr/share/scratch/Media/Sounds/Effects/Pop.wav`, `./Sounds/Effects/Rattle.wav`, `./Sounds/Human/FingerSnap.wav`, `./Sounds/Vocals/Singer1.wav`, `./Sounds/Animal/Goose.wav`