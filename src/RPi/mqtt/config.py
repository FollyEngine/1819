

import yaml
import sys


#######
# load config (extract to lib)
configFile = "config.yml"


if len(sys.argv) > 1:
    configFile = sys.argv[1]

with open(configFile, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


def getValue(name, default):
    if name in cfg and cfg[name] != "":
        return cfg[name]
    return default
