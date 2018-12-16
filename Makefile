
mqtt:
	mosquitto_sub -h mqtt.thegame.folly.site -v -t +/+/+ -u everyone -P S4C7Tzjc2gD92y9

post:
	mosquitto_pub -h mqtt.thegame.folly.site -u everyone -P S4C7Tzjc2gD92y9 -t asdf/asdf/asdf -m '{}'
