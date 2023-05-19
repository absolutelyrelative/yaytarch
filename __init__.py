import os
from flask import Flask
from . import db, collectionview
from yt_dlp import YoutubeDL
import click

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
    app.register_blueprint(collectionview.bp)
    app.add_url_rule('/', endpoint='index')

    @app.route('/')
    def hello():
        return "Hello."

    @app.cli.command("dl")
    @click.argument("link")
    def dl(link):
        locdict = {
            'home' : os.getcwd() + '\\videos\\'
        }
        output_template_dic = {
            'default' : "%(id)s.%(ext)s"
        }
        ytdlp_options = {'paths' : locdict, 'outtmpl' : output_template_dic}
        with YoutubeDL(ytdlp_options) as ydl:
            ydl.download(link)

    return app