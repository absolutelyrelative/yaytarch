import functools

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
