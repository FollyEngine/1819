#!/usr/bin/python3

import pyaudio
import wave
import dropbox
import sys
import paho.mqtt.client as mqtt
import threading
import lameenc

node = "twotwo"
if len(sys.argv) > 1:
    node = sys.argv[1]

record_secs = 3
sample_rate = 44100
chunk = 4096

recording = threading.Event()
stop_recording = threading.Event()

def record_some_audio():
    recording.set()
    print("Starting recording...")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, rate=sample_rate, channels=1, \
                        input_device_index=1, input=True, \
                        frames_per_buffer=chunk)
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(128)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(2)
    stop_recording.clear()
    mp3_data = bytearray()
    while not stop_recording.isSet():
        data = stream.read(chunk)
        mp3_data += encoder.encode(data)
    mp3_data += encoder.flush()
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print("Uploading to Dropbox...")
    dbx = dropbox.Dropbox("lDJLfPyGGqAAAAAAAAAADeav0BmGxuaz7g52YhSNybYqTbIaHhfh8RiSzK4IkNbC")
    dbx.files_upload(bytes(mp3_data), "/dream.mp3", autorename=True)
    print("Uploading done")
    recording.clear()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(node + "/#")

def on_message(client, userdata, msg):
    if msg.topic == "twotwo/start-recording":
        if recording.isSet():
            print("Already recording!")
        else:
            threading.Thread(target=record_some_audio).start()
    elif msg.topic == "twotwo/stop-recording":
        print("Stopping recording..")
        stop_recording.set()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt", 1883, 60)
client.loop_forever()
