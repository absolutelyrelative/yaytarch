from .model import collectionmodel
from flask import (
    Blueprint, render_template
)

from .model import collectionmodel
from .model import videocollectionrelmodel as videocollectionmembershipmodel

# This blueprint shows all the available collections and any future feature related to collections

bp = Blueprint('collections', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    collections = collectionmodel.getallcollections()

    return render_template('collections.html', collections=collections)


@bp.route('/collection/<int:collectionid>')
def viewcollection(collectionid):
    videos = videocollectionmembershipmodel.getvideocollectionmembershipbyid(collectionid, type="COLLECTION")

    return render_template('videolist.html', videos=videos)
