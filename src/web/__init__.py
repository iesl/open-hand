import os

from flask import Flask

# from sassutils.wsgi import SassMiddleware

from flask_assets import Environment
from .util.assets import bundles

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import home

    app.register_blueprint(home.bp)
    app.add_url_rule("/", endpoint="index")

    assets = Environment(app)
    # js = Bundle('jquery.js', filters='jsmin', output='gen/packed.js')
    # assets.register('js_all', js)
    assets.register(bundles)

    # app.wsgi_app = SassMiddleware(app.wsgi_app, {
    #     'myapp': ('static/sass', 'static/css', '/static/css')
    # })

    return app
