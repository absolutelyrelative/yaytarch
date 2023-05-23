import functools, click
from yt_dlp import YoutubeDL

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)

from yaytarch.db import get_db
import os

#This blueprint takes care of the video view page and any future feature of it

bp = Blueprint('videos', __name__)

@bp.route('/video/<int:video_id>')
def viewvideo(video_id):
    db = get_db()

    videos = db.execute('SELECT * FROM video WHERE video.id = ' + str(video_id)
    ).fetchall()

    return render_template('videoplay.html', videos = videos)

@bp.route("/video/source/<int:video_id>")
def load_video(video_id):
    db = get_db()
    video = db.execute('SELECT loc FROM video WHERE video.id = ' + str(video_id)
    ).fetchone()
    location_from_db = video['loc']

    file_name = os.path.basename(location_from_db)
    dir_name = os.path.dirname(location_from_db)

    return send_from_directory(dir_name, file_name)


@bp.cli.command("dl")
@click.argument("link")
def dl(link):
    coolkeys = ['id', 'title', 'thumbnail', 'description', 'format', 'format_id', 'ext', 'width', 'height', 'resolution']

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
        #TODO: Investigate why 'release_date' in coolkeys throws error in dict. Maybe it is missing?
        subdct = {key: dict_dump[key] for key in coolkeys}
        ydl.download(link)
        registervideo(subdct, locdict)
    
def registervideo(dict, locdict):
    db = get_db()
    loc = locdict['home'] + dict['id'] + '.' + dict['ext']
    print('location: ' + loc)

    try:
        db.execute(
            "INSERT INTO video (shorturl, loc, downloaded, title, width, height, descr, resolution) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (dict['id'], loc, 1, dict['title'], dict['width'], dict['height'], dict['description'], dict['resolution']),
        )
        db.commit()
    except db.IntegrityError:
        print("oops")
    else:
        pass

    #TODO: Pass into its own generalised function with automatic ID detection
    # this is just to make testing easier for the moment
    
    #Add to 'All' category automatically
    print(dict['id'])
    video = db.execute('SELECT id FROM video WHERE video.shorturl = "' + dict['id'] + '"'
    ).fetchone()
    videokey = video['id']
    try:
        db.execute(
            "INSERT INTO videocollectionmembership (videoid, collectionid) VALUES (?, ?)",
            (videokey,1),
        )
        db.commit()
    except db.IntegrityError:
        print("oops")
    else:
        pass