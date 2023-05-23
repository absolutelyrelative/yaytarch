import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)

from yaytarch.db import get_db
import os

#This blueprint shows all the available collections and any future feature related to collections

bp = Blueprint('collections', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()

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