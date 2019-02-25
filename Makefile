
sub:
	mosquitto_sub -d -h localhost -v -t +/+/+ 

mqtt:
	mosquitto_sub -d -h mqtt.thegame.folly.site -v -p 8883 -t +/+/+ -u everyone -P S4C7Tzjc2gD92y9

site:
	mosquitto_pub -d -h mqtt.thegame.folly.site -p 8883 -u everyone -P S4C7Tzjc2gD92y9 -t asdf/asdf/asdf -m '{"to": "folly.site"}'

local:
	mosquitto_pub -h localhost -t asdf/asdf/asdf -m '{"to": "folly.site"}'
