import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
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
    return ('You asked for collection{0}'.format(collection_id))
""" https://stackoverflow.com/questions/55961665/flask-wont-play-a-video-in-the-html """