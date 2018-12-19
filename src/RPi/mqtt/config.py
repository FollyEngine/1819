

import yaml
import sys
import os.path

#######
# load config (extract to lib)
configFile = "config.yml"
cfg = {}


if len(sys.argv) > 1:
    configFile = sys.argv[1]

if os.path.isfile(configFile):
    with open(configFile, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)


def getValue(name, default):
    if name in cfg and cfg[name] != "":
        return cfg[name]
    return default
