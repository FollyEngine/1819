# DMX controller

* [ ] beamZ PLS15 LED Strobe
* [ ] cheap 8 channel mini-PAR
* [ ] smoke machine 1
* [ ] smoke machine 2
* [ ] The other ones...

We've had Zero success using the Enttec OpneDMX USB controllers to talk to the beamZ and mini-PAR

So I took a set home, and connected them to my very cheap LIXADA USB DMX thing - and ...

## using LIXADA

Using the cmdline from https://github.com/dhocker/udmx-pyusb

for example, fully on, no flashing:

```
./uDMX 1 255
./uDMX 2 0
```

* beamZ strobe WORKS.
   * channel 0 == intensity
   * channel 1 == speed
* mini-PAR - same result as Teegan - its still in sound mode.