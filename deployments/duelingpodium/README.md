# 2 dualling podiums

2 time each.....

## RPi connected to:

* [x] Yellow D10x UHF rfid reader
* [x] powered speaker using PHAT-DAC (works)
* neopixel on rpi proto board to show  (some code)
  * [x] health bar (16 pixels)
* [x] mifare rfid reader (works)
* [x] USB power


## ESP32
* [x] touch sensors - 5 selectors
* [x] [touch arduino sketch](../src/wemos/wemos_button/wemos_button.ino)
* [x] USB power

## shaker controller
* [ ] wemos mini boards with ir control...
* [ ] [ir relay arduino sketch](../src/wemos/wemos_ir/wemos_ir.ino)
* [x] USB power


## Microservices:

* [x] [d10x rfid event source](../../src/RPi/rfid-d10x/main.py)
* [x] [mifare rfid event source](../../src/RPi/rfid-mifare/main.py)
* [x] [audio player sink](../../src/RPi/audio/main.py)
* [x] [neopixel sink](../../src/RPi/neopixels/main.py) (not sure - this may running one per neopixel string with cfg?)
* [ ] [podium controller generated from designer](../../controller/podium/main.py)


## initial testing controller:

1. waits for a user to "login" using their personal mifare tag
2. displays user's health
3. waits for wand/orb/magic item to be registered as cast using the UHF reader
4. plays magic audio - `/usr/share/scratch/Media/Sounds/Effects/Pop.wav`, `./Sounds/Effects/Rattle.wav`, `./Sounds/Human/FingerSnap.wav`, `./Sounds/Vocals/Singer1.wav`, `./Sounds/Animal/Goose.wav`

## What actually happens.

1. user scans on bottom of wand (nfc)
2. lookup wand info
3. set health to 100 and display on healthbar
4. user holds one of the modifier stones
5. user casts wand using yellow UHF reader
6. (other user does too - with timeout whish implies the other user loses)
7. sounds play, lights light, effects happen
8. combat maths decides who won, and what damage gets taken from users health
9. repeat until one user's health <= 0