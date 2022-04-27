
import typing as t

from .data import Config, ConfigSchema
from .log import logger

import os
import json

def setenv(env: str):
    os.environ['env'] = env

def getenv():
    return os.environ['env']

def load_config() -> t.Optional[Config]:
    config: t.Optional[Config] = None
    env = getenv()
    config_filename = f"config-{env}.json"
    workingdir = os.path.abspath(os.curdir)
    config_path = os.path.join(workingdir, config_filename)
    while workingdir != "/":
        logger.debug(f"Looking for config '{config_filename}' in {workingdir}")
        config_path = os.path.join(workingdir, config_filename)
        if os.path.exists(config_path):
            logger.info(f"Loading config '{config_path}'")
            with open(config_path) as f:
                jsonContent = json.load(f)
                loaded: Config = ConfigSchema().load(jsonContent)
                config = loaded
            break
        workingdir = os.path.abspath(os.path.join(workingdir, os.pardir))
    else:
        logger.warn(f"Could not find config {config_filename}")


    return config
