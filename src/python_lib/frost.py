# Utility file to load all the necessary modules, libraries, and environment settings for the Frost environment.

import logging
import yaml
import os 
import sys
import importlib

for file in os.listdir(os.path.dirname(__file__)):
    if file.startswith("LinguaFranca") and file.endswith(".so"):
        base_name = file[:-3]  
        base_module = importlib.import_module(base_name)
        break

from time_utils import TimePrecision
from l_formatter import LFormatter    
from machine_data_model.protocols.frost_v1.frost_message import FrostMessage


# load configuration file
FROST_CONFIG = os.environ.get("FROST_CONFIG", "resources/frost_config.yml")

# if the file does not exist, use a default configuration
if not os.path.exists(FROST_CONFIG) or not os.path.isfile(FROST_CONFIG):
    FROST_CONFIG = {
        "time_precision": "NSECS",
        "logging_level": "WARNING"
    }
else:
    with open(FROST_CONFIG) as config_file:
        FROST_CONFIG = yaml.safe_load(config_file)

TIME_PRECISION = TimePrecision[FROST_CONFIG["time_precision"]]
LOGGING_LEVEL = FROST_CONFIG["logging_level"].upper()

# setup logging
handler = logging.StreamHandler()
handler.setFormatter(LFormatter(base_module.time.logical_elapsed, TIME_PRECISION))
logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)
# Add the handler only if it hasn't been added yet
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(handler)

def is_target_valid(message: tuple[int, FrostMessage], target: str) -> bool:
    """Check if the target of the message matches the given target.
    Args:
        message (tuple[int, FrostMessage]): The message to check.
        target (str): The target to compare against.
    Returns:
        bool: True if the target matches, False otherwise.
    """
    message_target = message[1].target
    return message_target == target

