# Cauldron

RPi connected to:

* Yellow D10x UHF rfid reader
* powered speaker using PHAT-DAC
* string of neopixels - connected to RPi protoboard
* USB power


Microservices:

* [d10x rfid event source](../../src/RPi/rfid-d10x/main.py)
* [audio player sink](../../src/RPi/audio/main.py)
* [neopixel sink](../../src/RPi/neopixels/main.py)
* [cauldron controller generated from designer](../../controller/cauldron/main.py)