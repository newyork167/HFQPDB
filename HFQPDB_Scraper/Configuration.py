import ConfigParser
import os
import logging, sys

# Get the working directory to open the configuration file
working_directory = "/".join(os.path.realpath(__file__).split('/')[:-1]) + "/"

# Instantiate the ConfigParser object
config = ConfigParser.ConfigParser()

# Read the config file
try:
    config.read(working_directory + "config.ini")
except Exception as ex:
    print("Could not open configuration file. See example config for setup information.")
    sys.exit(100)

TESTING = False

# Determine the level of logging that we want
try:
    if config.getboolean("testing", "debug_logging_enabled"):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    if config.getboolean("testing", "testing"):
        TESTING = True
except:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def get(section, option):
    return config.get(section=section, option=option)


def getint(section, option):
    return config.getint(section=section, option=option)


def getboolean(section, option):
    return config.getboolean(section=section, option=option)


def getfloat(section, option):
    return config.getfloat(section=section, option=option)


def get_workingdir(section, option):
    return working_directory + config.get(section=section, option=option)
