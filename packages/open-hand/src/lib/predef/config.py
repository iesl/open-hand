import typing as t
from typing import Optional
import os
import json

from marshmallow import Schema, fields, post_load
from dataclasses import dataclass

from .schemas import StrField
from .log import logger


@dataclass
class OpenReviewConfig:
    restApi: str
    restUser: str
    restPassword: str


class OpenReviewSchema(Schema):
    restApi = StrField
    restUser = StrField
    restPassword = StrField

    @post_load
    def make(self, data: t.Any, **_) -> OpenReviewConfig:
        return OpenReviewConfig(**data)


@dataclass
class Config:
    openreview: OpenReviewConfig


class ConfigSchema(Schema):
    openreview = fields.Nested(OpenReviewSchema)

    @post_load
    def make(self, data: t.Any, **_) -> Config:
        return Config(**data)


def setenv(env: str):
    os.environ["env"] = env


def getenv():
    return os.environ["env"]


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


global_app_config: Optional[Config] = None


def get_config() -> Config:
    global global_app_config
    if global_app_config is None:
        global_app_config = load_config()
    if global_app_config is None:
        raise Exception("Config file could not be loaded")

    return global_app_config
