import os.path

from .tools.outputformat import bcolors
from .model import collectionmodel
from .model import collectionmodel
from .model import videocollectionrelmodel as videocollectionmembershipmodel
from .model import videomodel
from .tools import videodownload
from flask import (
    Blueprint, render_template, request, send_from_directory
)

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
                # TODO: Test if after creating this local collection updates it well
                newcollection = collectionmodel.videocollection(0, collectionurl, collectionname, "Local", "",
                                                                "", "", "", "", "")

                if collectionmodel.createvideocollectionentry(newcollection) is not None:  # Collection created
                    print(bcolors.OKGREEN + "Local collection created." + bcolors.ENDC)
                else:
                    print(
                        bcolors.WARNING + "Could not create collection. Make sure it is not a duplicate name." + bcolors.ENDC)
            # Collection with the name has been found
            else:
                print(
                    bcolors.WARNING + "Could not create collection. Make sure it is not a duplicate name." + bcolors.ENDC)

        # Request type: remove
        if 'collectionnametoremove' in request.form.keys():
            collectionname = request.form['collectionnametoremove']
            collectionobj = collectionmodel.findcollectionbyname(collectionname)  # Fetch collection object from name
            if collectionobj is not None:
                # fetch videos from collection
                videolist = videocollectionmembershipmodel.getvideocollectionmembershipbyid(collectionobj.id,
                                                                                            "COLLECTION")
                # attempt to move videos to "All Videos" playlist. Done outside the loop to save some computational power.
                allvideoscollection = collectionmodel.findcollectionbyname("All videos")
                for video in videolist:
                    videomodel.addvideotocollection(video.id, allvideoscollection.id)

                # attempt to remove all collection, video relationships and the collection entry itself
                if videocollectionmembershipmodel.removeallcollectionentries(
                        collectionobj.id) is not None and collectionmodel.removecollection(
                        collectionobj.id) is not None:
                    print(bcolors.OKGREEN + "Collection removed." + bcolors.ENDC)
                else:
                    print(
                        bcolors.WARNING + "Could not delete collection. Check terminal for more information." + bcolors.ENDC)

    collections = collectionmodel.getallcollections()
    return render_template('collections.html', collections=collections)


# TODO: Refactor with a more consistent argument passing
@bp.route('/collection/<int:collectionid>', methods=['GET', 'POST'])
def viewcollection(collectionid):
    if request.method == 'POST':

        # Request type: add video in collection
        if 'videourl' in request.form.keys():
            try:
                collectionname = collectionmodel.getvideocollectionbyid(collectionid).title
            except:
                print("Collection not found")  # Temporary solution
            videourl = request.form['videourl']
            videodownload.dl(videourl, collectionname)

        # Request type: refresh collection
        if 'buttonrefresh' in request.form.keys():
            videodownload.dlplaylistbyid(collectionid)



    videos = videocollectionmembershipmodel.getvideocollectionmembershipbyid(collectionid, type="COLLECTION")
    return render_template('videolist.html', videos=videos)


@bp.route("/collection/source/thumb/<int:collectionid>")
def load_picture(collectionid):
    collection = collectionmodel.getvideocollectionbyid(collectionid)
    dirname = os.path.dirname(collection.thumbnail)
    filename = os.path.basename(collection.thumbnail)

    return send_from_directory(dirname, filename)
