
from flask_assets import Bundle


bundles = {
    # 'home_js': Bundle(
    #     # filters='jsmin'
    #     output='gen/home.%(version)s.js'
    # ),

    'home_css': Bundle(
        'css/app.css',
        'sass/main.scss',
        filters='libsass',
        output='gen/home.%(version)s.css'
    ),
}
