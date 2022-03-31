from pathlib import Path
from flask_assets import Bundle

from lib import consts
from lib.log import logger


output_root = consts.ASSET_BUILD_PATH.relative_to(consts.PRJ_ROOT_PATH)

logger.info(f"Setting SASS output path to {output_root}")
CSS_OUTPUT = f"{output_root}/app.%(version)s.css"

home_css = Bundle(
    "css/app.css",
    "sass/main.scss",
    filters="libsass",
    output=CSS_OUTPUT,
    # output="gen/home.%(version)s.css",
)

watch = Path("sass/inc/*")
home_css.depends.append(watch)

bundles = {"home_css": home_css}

# 'home_js': Bundle( filters='jsmin' output='gen/home.%(version)s.js')
