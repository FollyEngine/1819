# timer direction and speed switches

remote from the dualing center, so

* RPi
* USB power
* USB mobile data - telstra usb stick (needs testing)
* switch connected to RPi proto board


microservice

* [switch controller generated from designer](../../controller/switch/main.py)
* [switch event source](../../src/RPi/switch/main.py)
* [mqtt proxy](../../src/RPi/proxy/main.py) - used to replicate some messages between local mqtt and the internet based thegame.folly.site mqtt server
