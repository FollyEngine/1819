# timer direction and speed switches

remote from the dualing center, so

* [x] RPi
* [x] USB power
* [x] USB mobile data - telstra usb stick
* [ ] switch connected to RPi proto board


microservice

* [switch controller generated from designer](../../controller/switch/main.py)
* [switch event source](../../src/RPi/switch/main.py)
* [mqtt relay](../../src/RPi/mqtt/main.py) - used to replicate some messages between local mqtt and the internet based thegame.folly.site mqtt server
