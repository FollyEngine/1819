
import socket
import yaml
import sys
import os.path
import logging

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
        logging.error("need to specify config options")
        logging.error("       %s <hostname> <deploymenttype> <devicename>" % sys.argv[0])
        exit()
    hostname=socket.gethostname()
    if args:
        hostname=sys.argv[1]
    return getValue("hostname", hostname)

def getDeploymentType():
    return sys.argv[2]

def getDevicename():
    return sys.argv[3]

#######
# load config (extract to lib)
configFile = "config.yml"
cfg = {}

logFile = sys.argv[0].replace("/", "-").replace(".py", ".log").replace(".-", "")
logging.basicConfig(
     level=getValue("loglevel", logging.DEBUG),
 )

# Create handlers
#c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(logFile)
#c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.DEBUG)
# Add handlers to the logger
logger = logging.getLogger()
#logger.addHandler(c_handler)
logger.addHandler(f_handler)

if os.path.isfile(configFile):
    with open(configFile, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        logging.debug("config.yml == %s" % cfg)
