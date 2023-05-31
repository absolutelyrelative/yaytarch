import os

from flask import Flask

from . import db, videocollections, videos


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='tempchange',
        DATABASE=os.path.join(app.instance_path, 'db.sqlite')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(videocollections.bp)
    app.register_blueprint(videos.bp, cli_group=None)
    app.add_url_rule('/', endpoint='index')

    return app
