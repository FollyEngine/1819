#!/usr/bin/python
import pysimpledmx

# try to talk to the enntec opendmx usb
# https://github.com/c0z3n/pySimpleDMX/

mydmx = pysimpledmx.DMXConnection("/dev/ttyUSB0")

# set DMX channel 1 to full
#mydmx.setChannel(1, 255)
# set DMX channel 2 to 128
#mydmx.setChannel(1, 228, True)
mydmx.setChannel(500, 228, True)
mydmx.setChannel(500, 228, True)
#mydmx.setChannel(3, 0)   # set DMX channel 3 to 0
#render    # render all of the above changes onto the DMX network
#mydmx.render()

#mydmx.setChannel(4, 255, autorender=True) # set channel 4 to full and render to the network
