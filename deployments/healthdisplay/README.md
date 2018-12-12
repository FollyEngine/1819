# health display

** how many, and where

Identify a person... MiFare RFID?

The one I've given James as a single white neopixel stack.
I hope to build a different one with 4 stacks, and the desktop UHF reader

* RPi
* miFare USB reader
* proto board connected to a number of noepixel displays
* USB power



Microservices:

* [x] [mifare rfid event source](../../src/RPi/rfid-mifare/main.py)
* [x] [neopixel sink](../../src/RPi/neopixels/main.py)
* [health controller generated from designer](../../controller/health/main.py)
