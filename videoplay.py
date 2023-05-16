import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from yaytarch.db import get_db

bp = Blueprint('watch', __name__)

@bp.route('/watch', methods=('GET', 'POST'))
def watch():
    return render_template('videoplay.html')

""" https://stackoverflow.com/questions/55961665/flask-wont-play-a-video-in-the-html """