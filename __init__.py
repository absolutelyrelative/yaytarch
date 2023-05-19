import os
from flask import Flask
from . import db, collectionview
from yt_dlp import YoutubeDL
import click
from yaytarch.db import get_db
import json

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
        coolkeys = ['id', 'title', 'thumbnail', 'description', 'release_date', 'format', 'format_id', 'ext', 'width', 'height', 'resolution']

        locdict = {
            'home' : os.getcwd() + '\\videos\\'
        }
        output_template_dic = {
            'default' : "%(id)s.%(ext)s"
        }
        ytdlp_options = {'paths' : locdict, 'outtmpl' : output_template_dic, 'format': 'mp4'}
        with YoutubeDL(ytdlp_options) as ydl:
            info = ydl.extract_info(link, download=False)
            dict_dump = ydl.sanitize_info(info)
            subdct = {key: dict_dump[key] for key in coolkeys}
            ydl.download(link)
            registervideo(dict_dump, locdict)
    
    def registervideo(dict, locdict):
        db = get_db()
        loc = locdict['home'] + dict['id'] + '.' + dict['ext']
        print('location: ' + loc)

        try:
            db.execute(
                "INSERT INTO video (shorturl, loc, downloaded) VALUES (?, ?, ?)",
                (dict['id'], loc, 1),
            )
            db.commit()
        except db.IntegrityError:
            print("oops")
        else:
            pass
    
    return app