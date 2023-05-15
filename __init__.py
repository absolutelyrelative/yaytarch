import os
from flask import Flask
from . import db

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
        
    """     #
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    # """


    @app.route('/')
    def hello():
        return "Hello."

    return app