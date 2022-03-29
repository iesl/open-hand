from pathlib import Path
from flask_assets import Bundle

home_css = Bundle(
    "css/app.css",
    "sass/main.scss",
    filters="libsass",
    output="gen/home.%(version)s.css",
)

watch = Path("sass/inc/*")
home_css.depends.append(watch)

bundles = {"home_css": home_css}

# 'home_js': Bundle( filters='jsmin' output='gen/home.%(version)s.js')
