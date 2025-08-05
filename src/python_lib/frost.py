# Utility file to load all the necessary modules, libraries, and environment settings for the Frost environment.

import logging
import yaml
import os 
import LinguaFrancaMain as lf
from time_utils import TimePrecision, convert, f_convert
from l_formatter import LFormatter    


# load configuration file
FROST_CONFIG = os.environ.get("FROST_CONFIG", "resources/frost_config.yml")

print(f"Loading FROST configuration from {FROST_CONFIG}")
# print current working directory
print(f"Current working directory: {os.getcwd()}")


# if the file does not exist, use a default configuration
if not os.path.exists(FROST_CONFIG) or not os.path.isfile(FROST_CONFIG):
    FROST_CONFIG = {
        "time_precision": "NSECS",
        "logging_level": "INFO"
    }
else:
    with open(FROST_CONFIG, "r") as config_file:
        FROST_CONFIG = yaml.safe_load(config_file)

TIME_PRECISION = TimePrecision[FROST_CONFIG["time_precision"]]
LOGGING_LEVEL = FROST_CONFIG["logging_level"].upper()

# setup logging
handler = logging.StreamHandler()
handler.setFormatter(LFormatter(lf.time.logical_elapsed, TIME_PRECISION))
logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)
logger.addHandler(handler)