from pathlib import Path
from flask_assets import Bundle

from lib.predef import consts
from lib.predef.log import logger

output_root = consts.ASSET_BUILD_PATH.relative_to(consts.PRJ_ROOT_PATH)

logger.info(f"Setting SASS output path to {output_root}")
CSS_OUTPUT = f"{output_root}/app.%(version)s.css"
JS_OUTPUT = f"{output_root}/app.%(version)s.js"

home_css = Bundle(
    "css/app.css",
    "sass/main.scss",
    filters="libsass",
    output=CSS_OUTPUT,
)

watch = Path("sass/inc/*")
home_css.depends.append(watch)

home_js = Bundle(
    "js/app.js",
    output=JS_OUTPUT,
)

home_js.depends.append(Path("js/*"))

bundles = {"home_css": home_css, "home_js": home_js}
