# 2 dualling podiums

2 time each.....

RPi connected to:

* Long range UHF RFID reader
  * one SPARKFUN with external antenna
  * one serial reader with big antenna
* powered speaker using PHAT-DAC
* neopixel on rpi proto board to show 
  * 4xspell strength bars (16 pixels) and
  * health bar (16 pixels)
* mifare rfid reader
* USB power


ESP32?
* touch sensors - 3 or 4 selectors
* neopixels for lighting the buttons
* [touch arduino sketch](../src/wemos/wemos_button/wemos_button.ino)
* USB power

shaker controller
* i'm not sure - I think I have 2 esp8266 ir controller boards
* [ir relay arduino sketch](../src/wemos/wemos_ir/wemos_ir.ino)
* USB power


Microservices:

* Long range UHF reader (one of...)
  * [thinkmagic rfid event source](../../src/RPi/rfid-ThinkMagic/main.py)
  * [thinkmagic rfid event source](../../src/RPi/rfid-serial/main.py)
* [mifare rfid event source](../../src/RPi/rfid-mifare/main.py)
* [audio player sink](../../src/RPi/audio/main.py)
* [neopixel sink](../../src/RPi/neopixels/main.py) (not sure - this may running one per neopixel string with cfg?)
* [podium controller generated from designer](../../controller/podium/main.py)