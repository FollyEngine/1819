
# sounds!

the easiest way to test, is to run the audio controller on your system:

```bash
pwd
..../follyengine/1819/src/RPi
./audio/main.py
```

and then from another terminal, run

```bash
mosquitto_pub -h mqtt.local -t yoga260/audio/play -m '{"sound": "../../../sounds/Dueling/Failure.wav"}'
```

The `sound` value is a path relative to the RPi dir that we're starting the RPi tools from.