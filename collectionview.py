import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)

from yaytarch.db import get_db

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

@bp.route("/video/movie1")
def load_video():
    test1 = "C:/Users/Pawel/Downloads/"
    test2 = "movie.mp4"
    return send_from_directory(test1, test2)