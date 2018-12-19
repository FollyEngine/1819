switch notes:
18/12/2018 
made folder in 1819/src/RPi called Switch
added test.py, made a simple program to operate a circuit based on recieving input from a GPIO PIN
added main.py to 1819/deployments/switch, by copying main.py from /duelingpodium, changing the name to switch1.

First step was sending test message ot server via mosquito.

To first test if it was transmitting I deleted lines 95 & 97

hostmqtt.subscribeL(myHostname, 'rfid-nfc', "scan", show_health)

hostmqtt.subscribeL(myHostname, 'ThingMagic', "scan", magic_cast)

errors when trying to run directly: could not import yaml, mqtt or config

am now adding RPi folder to PATH, and adding a yaml module.

ran mqtt.py directly via Python command prompt, gave error : "no module named paho.mqtt.client"

installing paho.mqtt using pip
in Python command, successfully able to import mqt and config however confign needed yaml
installing yaml with pip

while in ..//switch ran 
import yaml
import config
import qtt
successfully in python  command line.

However when navigating to deployments/switch, unable to run main.py due to error : "no module named config.py"

Identical file was placed in RPi/switch, and ran successfully. Test message was finally sent successfully.

The directory with config.py was added to the PATH variable so it could be accessed from RPi/switch/main.py 
however the same error was encountered. "no module named config.py"
more attempts were made to add to the variable PATH but each unsuccessful

for run.sh in deployments/switch it was run from /1819 using ./deployments/switch/run.sh --setup with lots of things hapening
its possibe that using --setup will help run main.y corredctly

using ./deployments/switch/run.sh --setup a second time was different, and successfully installed lots ofstuff

was prompted for reboot, accepted.

upon restart, navigated to /1819 and input /home/pi/1819/deployment/switch.run.sh

test message was delivered successfully! 

ON mosquito feed, reads: switch1/relay_from/status {"time": "2018-12-1909:123;123;123;12;31;23123", "status": "listening", "device": "relay_from"}


