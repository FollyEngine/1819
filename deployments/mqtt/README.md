# mqtt host

the central communications for the system.
There can be only one :)

it needs to run where the ASUS wifi access point it

* [x] RPi
* [x] USB power
* [x] ASUS WIFI access point


microservices

* [the database](../../src/RPi/database/main.py)
* [mqtt relay](deployments/mqtt/main.py) - used to replicate some messages between local mqtt and the internet based thegame.folly.site mqtt server
