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


## starting with a new RPi

I've been using `sudo dd of=/dev/mmcblk0 if=2018-04-18-raspbian-stretch-lite.img bs=4096` from my Linux box
to initialise a new sdcard. All the RPi's that were used previously in the convicts hope show are still the
same, just upgraded.

* change the `pi` user password to the common one...
* change `/etc/hostname` and `/host/hosts` to the new name
* install sshd! `apt-get update && apt-get install -yq openssh-server && apt-get -yq upgrade`
* `sudo raspi-config` to fix the keyboard, wifi, tz, enable sshd
* reboot :)
* install git `apt-get install -yq git`
* wpa_supplicant settings: `/etc/wpa_supplicant/wpa_supplicant.conf`:

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB

network={
	ssid="XXXXXXXXXXXX"
	psk="XXXXXXXXXXXXX"
}
```

apt-get everything:

```
apt-get install -yq openssh-server git mosquitto mosquitto-clients dnsmasq hostapd 
```


on the mqtt server, `apt-get install mosquitto mosquitto-clients`

## and the cheap router i have is too dumb to do dns, so setting up an rpi to be mqtt and wifi ap.

https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

```
sudo bash
apt-get install -yq dnsmasq hostapd
echo "interface wlan0
     static ip_address=192.168.4.1/24
     nohook wpa_supplicant" >> /etc/dhcpcd.conf
service dhcpcd restart
mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
echo "interface=wlan0      # Use the require wireless interface - usually wlan0
  dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" >> /etc/dnsmasq.conf
echo 'interface=wlan0
driver=nl80211
ssid=XXXXXXXXXXXXXX
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=XXXXXXXXXXXXXX
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP' >> /etc/hostapd/hostapd.conf

echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' >> /etc/default/hostapd

sudo systemctl start hostapd
sudo systemctl start dnsmasq

echo net.ipv4.ip_forward=1 >> /etc/sysctl.conf

iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
sh -c "iptables-save > /etc/iptables.ipv4.nat"
iptables-restore < /etc/iptables.ipv4.nat



```
