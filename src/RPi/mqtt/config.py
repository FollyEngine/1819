
import socket
import yaml
import sys
import os.path

#######
# load config (extract to lib)
configFile = "config.yml"
cfg = {}


#if len(sys.argv) > 1:
#    configFile = sys.argv[1]

if os.path.isfile(configFile):
    with open(configFile, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        print(cfg)


def getValue(name, default):
    if name in cfg and cfg[name] != "":
        return cfg[name]
    return default

def getHostname(args=True):
    # need to run all components with arguments:
    # <hostname>, <deploymenttype>, <devicename>
    # that way we know what our config.json settings are...
    # I'm thinking about allowing a host to run more than one deployment type at the same time
    if args and len(sys.argv) != 4:
        print("ERROR: need to specify config options")
        print("       %s <hostname> <deploymenttype> <devicename>" % sys.argv[0])
        exit()
    hostname=socket.gethostname()
    if args:
        hostname=sys.argv[1]
    return getValue("hostname", hostname)

def getDeploymentType():
    return sys.argv[2]

def getDevicename():
    return sys.argv[3]



