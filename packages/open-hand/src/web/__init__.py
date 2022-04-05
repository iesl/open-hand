import os

from flask import Flask

from flask_assets import Environment

from lib.consts import ASSET_BUILD_PATH, ASSET_CACHE_PATH, WEB_INSTANCE_PATH
from .util.assets import bundles

from lib.log import logger
from pprint import pp


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False, instance_path=str(WEB_INSTANCE_PATH.resolve()))

    if test_config is None:
        # load the instance config, if it exists, when not testing
        logger.info(f"Using config 'config.py'")
        app.config.from_object("web.flask-config.TestConfig")
        pp(app.config)
    else:
        # load the test config if passed in
        logger.info(f"Using config '{test_config}'")
        app.config.from_mapping(test_config)

    # ensure the instance folder(s) exist
    try:
        logger.info(f"mkdir {app.instance_path}")
        os.makedirs(app.instance_path, exist_ok=True)
        logger.info(f"mkdir {ASSET_CACHE_PATH}")
        os.makedirs(ASSET_CACHE_PATH, exist_ok=True)
        logger.info(f"mkdir {ASSET_BUILD_PATH}")
        os.makedirs(ASSET_BUILD_PATH, exist_ok=True)
    except OSError as e:
        logger.warn(f"Error mkdir: {e}")
        pass

    from . import home

    app.register_blueprint(home.bp)
    app.add_url_rule("/", endpoint="index")

    assets = Environment(app)
    assets.register(bundles)
    assets.cache = ASSET_CACHE_PATH

    return app
