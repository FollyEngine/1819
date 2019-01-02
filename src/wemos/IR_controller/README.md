# IR controller for TOTEM wobbleboard
for arduino/wemos/LOLIN

The statuses you can pass are based on the graphics on the remote buttons:
"POWER","PLAY","PAUSE","BIG P","WALK","RUN","SPRINT"
the mqtt device is "wobbleboard"; the verb is "button" (i know, it's a noun, but it stands for "button press"); the command is in a json object named "status".  Test like this:
`mosquitto_pub -h "mqtt" -t "all/wobbleboard/button" -m '{"status":"SPRINT","device":"thegame","time":"2018-12-22T06:17:40"}'`

Don't use "POWER" because it is a toggle switch with no feedback, no way of knowing whether the power is off or on
On the factory remote:
* You must press "PLAY" before you can press "WALK", "RUN", or "SPRINT"
* You must press "PAUSE" to stop, and the board slows gradually.  
* When you press "PLAY" again the board starts at the slowest speed
In this program:
* When you send "WALK", "RUN", or "SPRINT" we send a "PLAY" signal first
..* so the only statuses you need are "WALK", "RUN", "SPRINT", "PAUSE"

The LOLIN device should be 
* directly above the board
* up to three metres away, but that reduces to one if it's at an angle
* facing in any direction (there are 4 IR lights on the device).
* in direct line of sight.
The PAUSE command is most sensitive, other commands work twice as far away.
The board beeps whenever you send a signal.  there is no volume control

