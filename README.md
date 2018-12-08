# 1819
track all the parts we need to build

The `src` contains the source for the `RPi` microservices, and the `wemos` arduino sketches.

Each RPi will have a directory in the `deployments` directory, which will define which microservices are running on it, and other location / prop specific settings, files and details.

## Some of the plan

Most of the hardware will be at the game HQ, so I'm planning to put a good WIFI router there,
that all the local devices will connect to. There will also be a dedicated mqtt server, and controller there
with all other RPi's and esp(9266/32)'s talking to it. There is expected to be good internet connectivity
to talk to the offsite mqtt server.

There are expected to be 4 sites that are separate, and are expected to only have a puzzle toggle switch
that is connected to an RPi that has a telstra mobile data usb stick in it.
