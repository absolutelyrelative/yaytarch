import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from yaytarch.db import get_db

#This blueprint shows all the available collections

bp = Blueprint('collections', __name__)

@bp.route('/collections', methods=('GET', 'POST'))
def collections():
    db = get_db()
    error = None #Will be used to show if there are no collections
    collections = db.execute(
        'SELECT * FROM videocollection'
    ).fetchall()

    for rows in collections:
        for columns in collections[rows]:
            print(columns)

    return render_template('collections.html')

""" https://stackoverflow.com/questions/55961665/flask-wont-play-a-video-in-the-html """