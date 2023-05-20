import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)

from yaytarch.db import get_db
import os

#This blueprint shows all the available collections

bp = Blueprint('collections', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    error = None #Will be used to show if there are no collections
    collections = db.execute(
        'SELECT * FROM videocollection'
    ).fetchall()

    return render_template('collections.html', collections = collections)

@bp.route('/collection/<int:collection_id>')
def viewcollection(collection_id):
    db = get_db()
    videos = db.execute(
        'SELECT * FROM video WHERE video.id IN (SELECT videoid FROM videocollectionmembership WHERE videocollectionmembership.collectionid = ' + str(collection_id) + ');'
    ).fetchall()

    return render_template('videolist.html', videos = videos)


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
