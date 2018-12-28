#!/usr/bin/python
import pysimpledmx
import time
# try to talk to the enntec opendmx usb
# https://github.com/c0z3n/pySimpleDMX/


mydmx = pysimpledmx.DMXConnection("/dev/ttyUSB1")
def setallzero():
	print("reset everything to zero")
	for i in range(2,50):
		mydmx.setChannel(i, 0)
		mydmx.render()

setallzero() # why doesn't this work??
time.sleep(1)

## make everything red and flashy
print("strobe test") 
mydmx.setChannel(16, 255) # strobe2 intensity 
mydmx.setChannel(17, 255) # strobe2 strobe 
mydmx.setChannel(12, 255) # strobe1 strobe 
mydmx.setChannel(11, 255) # strobe1 intensity
mydmx.setChannel(21, 255)
mydmx.setChannel(22, 255)
mydmx.setChannel(37, 255)
mydmx.setChannel(31, 255)
mydmx.setChannel(46, 255) # smoke
mydmx.render()
time.sleep(3)
setallzero()



# strobe test ###############################
print("strobe test") 
mydmx.setChannel(12, 255) # intensity 
mydmx.setChannel(11, 255)
mydmx.render()
time.sleep(3)
setallzero()


print("other strobe test") 
mydmx.setChannel(16, 255) # intensity 
mydmx.setChannel(17, 255)
mydmx.render()
time.sleep(3)
setallzero()


# pin spot test #############################
# 21 is intensity
print ("pin spot")
print("21 + 22 makes red")
mydmx.setChannel(21, 255)
mydmx.setChannel(22, 255)
mydmx.render()
time.sleep(3)
setallzero()

print("21 + 23 makes green")
mydmx.setChannel(21, 255)
mydmx.setChannel(23, 255)
mydmx.render()
time.sleep(3)
setallzero()

print("21 + 24 makes blue")
mydmx.setChannel(21, 255)
mydmx.setChannel(24, 255)
mydmx.render()
time.sleep(3)
setallzero()

print("21 + 24 + 20 still makes blue")

print("21 + 25  makes white")
mydmx.setChannel(21, 255)
mydmx.setChannel(25, 255)
mydmx.render()
time.sleep(3)
setallzero()

print("21 + 20 makes nothing")

print("20 + 24 makes nothing")
mydmx.setChannel(20, 255)
mydmx.setChannel(24, 255)
mydmx.render()
time.sleep(3)
setallzero()

print ("test all pin spot")
for i in range(21,26):
	print(i)
	# set DMX channel  to full
	mydmx.setChannel(i, 255)
	mydmx.render()
	time.sleep(3)
print("off")
setallzero()

# parcan ########################################
print("30 + 37 makes nothing (channel 30 is not set)")

print("31 + 37 makes red")
mydmx.setChannel(37, 255)
mydmx.setChannel(31, 255)
mydmx.render()
time.sleep(3)
setallzero()

print("32 + 37 makes green")
mydmx.setChannel(37, 255)
mydmx.setChannel(32, 255)
mydmx.render()
time.sleep(1)
setallzero()

print("33 + 37 makes blue")
mydmx.setChannel(37, 255)
mydmx.setChannel(33, 255)
mydmx.render()
time.sleep(1)
setallzero()

print("38 + 37 does nothing (strobe without colour)")

print("36 + 37 in either order makes purple")
mydmx.setChannel(37, 255)
mydmx.setChannel(36, 255)
mydmx.render()
time.sleep(1)
setallzero()

print("35 + 37 in either order makes orange")
mydmx.setChannel(37, 255)
mydmx.setChannel(35, 255)
mydmx.render()
time.sleep(3)
setallzero()

print("34 + 37 in either order makes white")
mydmx.setChannel(37, 255)
mydmx.setChannel(34, 255)
mydmx.render()
time.sleep(1)
setallzero()




# parcan  test
# colours add.  so you have to set the last colour to 0 before you add a colour
# set DMX channel 36  (strobe intensity) to full.  nothing else works without that

print("parcan strobe test : intensity then colour cycle then strobe makes a blue strobe")
mydmx.setChannel(32, 255) #  
mydmx.setChannel(38, 255) # 
mydmx.setChannel(37, 255) # strobe
mydmx.render()
print("we should be strobing green (32,33,36,37,38")
time.sleep(3)
setallzero()

print("strobe test : intensity then colour cycle then strobe makes a blue strobe")
mydmx.setChannel(36, 255) # set intensity to a lot
mydmx.setChannel(37, 255) # strobe
mydmx.setChannel(38, 255) # colour cycle
mydmx.render()
print("we should be strobing purple (36,37,38")
time.sleep(3)
setallzero()




for i in range(2,50):
	print(i)
	# set DMX channel  to full
	mydmx.setChannel(i, 255)
	# set DMX channel  to 128
	#mydmx.setChannel(i, 228, True)
	#mydmx.setChannel(500, 228, True)
	#mydmx.setChannel(500, 228, True)
	#mydmx.setChannel(3, 0)   # set DMX channel 3 to 0
	#render    # render all of the above changes onto the DMX network
	mydmx.render()
	time.sleep(5)
	if i != 10 and i != 15 and i != 20 and i != 36:  # don't turn off the intensity channels
		mydmx.setChannel(i, 0)
setallzero()




#mydmx.setChannel(4, 255, autorender=True) # set channel 4 to full and render to the network

# 10	Strobe 1	Intensity
# 11	Strobe 1	Speed

# 15	Strobe 2	Intensity
# 16	Strobe 2	Speed

# 20	Pin spot	Intensity
# 21	Pin spot	Red
# 22	Pin spot	Green
# 23	Pin spot	Blue
# 24	Pin spot	White
# 25	Pin spot	Strobe
# 26	Pin spot	Colour cycle

# 30	Parcan	Red
# 31	Parcan	Green
# 32	Parcan	Blue
# 33	Parcan	White
# 34	Parcan	Amber
# 35	Parcan	UV
# 36	Parcan	Intenstity
# 37	Parcan	Strobe
# 38	Parcan	Colour cycle
# 39	Parcan	colour cycle speed
