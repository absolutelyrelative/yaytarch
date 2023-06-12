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
        # Request type: add
        if 'collectionnametoadd' in request.form.keys():
            collectionname = request.form['collectionnametoadd']
            collectionurl = request.form['collectionurltoadd']
            # No collection with the name has been found
            if collectionmodel.findcollectionbyname(collectionname) is None:
                # New collection object
                newcollection = collectionmodel.videocollection(0, collectionname, collectionurl)

                if collectionmodel.createvideocollectionentry(newcollection) is not None:  # Collection created
                    print(bcolors.OKGREEN + "Local collection created." + bcolors.ENDC)
                else:
                    print(
                        bcolors.WARNING + "Could not create collection. Make sure it is not a duplicate name." + bcolors.ENDC)
            # Collection with the name has been found
            else:
                print(
                    bcolors.WARNING + "Could not create collection. Make sure it is not a duplicate name." + bcolors.ENDC)

        # TODO: Create SQL to remove collection (pay attention to N to N relations)
        # Request type: remove
        if 'collectionnametoremove' in request.form.keys():
            collectionname = request.form['collectionnametoremove']
            collectionobj = collectionmodel.findcollectionbyname(collectionname)  # Fetch collection object from name
            if collectionobj is not None:
                # fetch videos from collection
                videolist = videocollectionmembershipmodel.getvideocollectionmembershipbyid(collectionobj.id, "COLLECTION")
                # attempt to move videos to "All Videos" playlist. Done outside the loop to save some computational power.
                allvideoscollection = collectionmodel.findcollectionbyname("All videos")
                for video in videolist:
                    videocollectionmembershipmodel.createvideocollectionmembershipentry(video.id, allvideoscollection.id)

                # attempt to remove all collection, video relationships and the collection entry itself
                # TODO: PROBLEM IS HERE: parameters are of unsupported type (removeallcollectionentries), maybe second one too
                if videocollectionmembershipmodel.removeallcollectionentries(collectionobj.id) is not None and collectionmodel.removecollection(collectionobj.id) is not None:
                    print(bcolors.OKGREEN + "Collection removed." + bcolors.ENDC)
                else:
                    print(bcolors.WARNING + "Could not delete collection. Check terminal for more information." + bcolors.ENDC)



    collections = collectionmodel.getallcollections()
    return render_template('collections.html', collections=collections)


@bp.route('/collection/<int:collectionid>')
def viewcollection(collectionid):
    videos = videocollectionmembershipmodel.getvideocollectionmembershipbyid(collectionid, type="COLLECTION")

    return render_template('videolist.html', videos=videos)
