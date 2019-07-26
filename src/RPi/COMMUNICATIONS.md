# MQTT based JSON

All the devices communicate on a shared MQTT bus using JSON formatted messages.
To simplify the microservice code, each host that is able, runs a local Mosquitto MQTT service that is set up to relay
messages from & to the global MQTT service at folly.site.

The high level game logic can be either encoded in controllers, as done in Woodford and a convict's hope, or built in NodeRed on our hosted Node Red server.

The communications protocol has grown organically, and needs to become codified to help interoperability.

I'd _like_ to head towards a message payload that resembles https://github.com/cloudevents/spec/blob/master/spec.md but it feels overly verbose.

## Existing messages

Generally, the MQTT message tag is used to identify who is expected to listen/receive the message, as that simplifies the subscription.

### Microservice Status message

On Start and Stop of a service, it sends out a status message

(`<devicename>` really means microservice name, as each microservice sends out a status)

Start:
```
tag: <hostname>/<devicename>/status
payload: 
{
    "device": "<devicename>",
    "time": "<date-time in isoformat>",
    "status": "listening",
}
```

Stop:
```
tag: <hostname>/<devicename>/status
payload: 
{
    "device": "<devicename>",
    "time": "<date-time in isoformat>",
    "status": "STOPPED",
}
```


There is no reply to the status (TODO: confirm this)

### Ping Service

To help debugging, the RPi's have a ping microservice (`ping/main.py`) that sends out a ping every second, and receives back a reply from Node-Red

Ping:
```
tag: node-red/status/ping
payload: 
{
    "device": "<devicename>",
    "time": "<date-time in isoformat>",
    "ping": "hello",
    "from": "<hostname>",
    "ip": "<ip address>",
    "git_commit": "<git-commit>",   
}
```

Reply (which the ping service listens for to extract the status colour):
```
tag: <origin-hostname>/<origin-device>/reply
payload: 
{
    "device": "<devicename>",
    "time": "<date-time in isoformat>",
    "status": "<colour-name>",

}
```

The microservice on the RPi's then sends out a message to that host's `neopixel-status` service to set one pixel to the status colour. If it times out waiting for a status reply, it will set the status to `red` and send that.

### neopixel service

neopixel code is reused several times with different `<devicename>`s:
* `neopixel-status`
* ....

Listens for:
```
tag: <hostname>/<devicename>/play
payload: 
{
    "device": "<devicename>",
    "time": "<date-time in isoformat>",
    "operation": "(set|health|colourwipe|theatrechase|rainbow|rainbowcycle|magic_item)",
    "colour": "<colour-name>",
    "count": "<pixel-count>",
}
```

magic_item adds the following extra fields which correspond to the colours (Air:white, Water:blue, Earth:green, Fire:red):
```
{
    "Air": <value-out-of-100>,
    "Water": <value-out-of-100>,
    "Earth": <value-out-of-100>,
    "Fire": <value-out-of-100>,
}
```
The neopixel display doesn't send a reply.

### audio service

The audio service is used to play wav/mp3 files that are already available on the RPi

The audiofile can either be a relative path from this repo's `sounds` dir, or an absolute path starting with `/`.

Listens for:
```
tag: <hostname>/<devicename>/play
payload: 
{
    "device": "<devicename>",
    "time": "<date-time in isoformat>",
    "sound": "<audiofilename>"
}
```
and
```
tag: <hostname>/<devicename>/mute
payload: 
{
    "device": "<devicename>",
    "time": "<date-time in isoformat>",
}
```
and
```
tag: <hostname>/<devicename>/unmute
payload: 
{
    "device": "<devicename>",
    "time": "<date-time in isoformat>",
}
```

When its finished playing the sound, the service will reply with:

replies with:
```
tag: <hostname>/<devicename>/played
payload: 
{
    "device": "<devicename>",
    "time": "<date-time in isoformat>",
    "status": "played",
    "sound": "<audiofilename>"
}
```
