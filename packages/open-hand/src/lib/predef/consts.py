from pathlib import Path
import os

SRC_ROOT_PATH = (Path(__file__) / os.pardir / os.pardir / os.pardir).resolve()
PRJ_ROOT_PATH = (SRC_ROOT_PATH / os.pardir).resolve()

WEB_ROOT_PATH = (SRC_ROOT_PATH / "web").resolve()
WEB_INSTANCE_PATH = (PRJ_ROOT_PATH / ".webapp-instance.d").resolve()

ASSET_BUILD_PATH = (WEB_INSTANCE_PATH / "asset-build.d").resolve()
ASSET_CACHE_PATH = (WEB_INSTANCE_PATH / "webassets-cache.d").resolve()

LIB_ROOT_PATH = (SRC_ROOT_PATH / "lib").resolve()
