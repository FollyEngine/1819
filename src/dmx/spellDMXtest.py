def stopthathorribleflashing():
    print("stoppit")
#    for i in range(2,50):
#     print(i)

def smokeyflashy(spellDMXcode):
    print("smokeyflashy")
    # TODO : loop through DMXcode array, set most of the things to zero and a couple to 255
    thisDMX=spellDMXcodes[spellDMXcode]
    print(thisDMX)
    for dmx in thisDMX:
      print(dmx)
    # TODO: wait four seconds.  how should we do that?  a callback?
    stopthathorribleflashing()

spellDMXcodes = {
"Fire": [31,46],
"Earth": [32,46],
"Water": [33,46],
"Air": [34,46],
"Lava": [31,32,46],
"Steam": [31,33,46],
"Wood": [32,34,46],
"Electricity": [31,33,46],
"Dust": [32,34,46],
"Ice": [33,34,46],
"Light": [35,46]
}
smokeyflashy("Ice")

stopthathorribleflashing()
