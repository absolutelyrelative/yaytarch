import functools
from .model import video as videomodel
from .model import collection as collectionmodel
from .model import videocollectionmembership as videocollectionmembershipmodel
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from yaytarch.db import get_db
import os

#This blueprint shows all the available collections and any future feature related to collections

bp = Blueprint('collections', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    collections = collectionmodel.getallcollections()

    return render_template('collections.html', collections = collections)

@bp.route('/collection/<int:collectionid>')
def viewcollection(collectionid):
    videos = videocollectionmembershipmodel.getvideocollectionmembershipbyid(collectionid, type="COLLECTION")

    return render_template('videolist.html', videos = videos)