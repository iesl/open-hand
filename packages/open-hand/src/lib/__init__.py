
from typing import Optional
from lib.predefs.config import load_config
from lib.predefs.data import Config

app_config: Optional[Config] = None

def get_config() -> Config:
    global app_config
    if app_config is None:
        app_config = load_config()
    if app_config is None:
        raise Exception("Config file could not be loaded")

    return app_config
