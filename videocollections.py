from tools.outputformat import bcolors
from .model import collectionmodel
from flask import (
    Blueprint, render_template, request
)

from .model import collectionmodel
from .model import videocollectionrelmodel as videocollectionmembershipmodel

# This blueprint shows all the available collections and any future feature related to collections

bp = Blueprint('collections', __name__)


# TODO: Use flask's flash to flash the error message instead of printing it to terminal.
@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'collectionname' in request.form.keys():  # Remove from playlist buttom
            collectionname = request.form['collectionname']
            # No collection with the name has been found
            if collectionmodel.findcollectionbyname(collectionname) is None:
                newcollection = collectionmodel.videocollection(0,collectionname,"0") #New collection object
                if collectionmodel.createvideocollectionentry(newcollection) is not None: #Collection created
                    print(bcolors.OKGREEN + "Local collection created." + bcolors.ENDC)
                else:
                    print(bcolors.WARNING + "Could not create collection. Make sure it is not a duplicate name." + bcolors.ENDC)
            # Collection with the name has been found
            else:
                print(bcolors.WARNING + "Could not create collection. Make sure it is not a duplicate name." + bcolors.ENDC)
    collections = collectionmodel.getallcollections()

    return render_template('collections.html', collections=collections)


@bp.route('/collection/<int:collectionid>')
def viewcollection(collectionid):
    videos = videocollectionmembershipmodel.getvideocollectionmembershipbyid(collectionid, type="COLLECTION")

    return render_template('videolist.html', videos=videos)
