# health display

** how many, and where

not sure - how do we identify a person... MiFare RFID?

* RPi
* miFare USB reader
* proto board connected to a number of noepixel displays
* USB power



Microservices:

* [mifare rfid event source](../../src/RPi/rfid-mifare/main.py)
* [neopixel sink](../../src/RPi/neopixels/main.py)
* [health controller generated from designer](../../controller/health/main.py)