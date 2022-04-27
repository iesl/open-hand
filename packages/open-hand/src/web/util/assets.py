from pathlib import Path
from flask_assets import Bundle

from lib.predefs import consts
from lib.predefs.log import logger

output_root = consts.ASSET_BUILD_PATH.relative_to(consts.PRJ_ROOT_PATH)

logger.info(f"Setting SASS output path to {output_root}")
CSS_OUTPUT = f"{output_root}/app.%(version)s.css"

home_css = Bundle(
    "css/app.css",
    "sass/main.scss",
    filters="libsass",
    output=CSS_OUTPUT,
)

watch = Path("sass/inc/*")
home_css.depends.append(watch)

bundles = {"home_css": home_css}
