# megagame health display

possibly lots


* [x] RPi
* [x] miFare USB reader to ID the magic item.
* [x] powered speaker using PHAT-DAC (works)
* [x] proto board connected to 
  * one 16 pixel noepixel display (pin 21) 
  * one 1 pixel noepixel display (pin 18) 
* [x] USB power



## Microservices:

* [x] [mifare rfid event source](../../src/RPi/rfid-mifare/main.py)
* [x] [audio player sink](../../src/RPi/audio/main.py)
* [x] [neopixel sink](../../src/RPi/megagame/main.py)
* [controller generated from designer](../../controller/megagame/main.py)  <--- replacing with nodered..

## Hardware manifest

Two versions - one using full size rpi, and one with rpi-zerow

### Full Size RPI

* ($99) RPi 3+
* wall wart
* ($) PHAT DAC 
* () Freetronics PiBreak Plus
* () pi stacking header
* () USB NFC reader
* () single neopixel for status
* () 2 8*neopixel bars soldered together

### RPI zero w

* ()  RPi zero
* () wall wart
* ($) PHAT DAC 
* () Adafruit rpi zero proto bonnet
* () microUSB hub or microUSB host adaptor
* () pi stacking header
* () USB NFC reader
* () single neopixel for status
* () 2 8*neopixel bars soldered together
