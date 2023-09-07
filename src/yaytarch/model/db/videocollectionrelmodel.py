# This module provides a class object for the M to M relationship between videos and collections in the database.
from . import collectionmodel, videomodel
from ...db import get_db
from ...tools.outputformat import bcolors


# CREATE TABLE videocollectionmembership (
#    videoid INTEGER NOT NULL,
#    collectionid INTEGER NOT NULL,
#    FOREIGN KEY (videoid) REFERENCES video (id),
#    FOREIGN KEY (collectionid) REFERENCES videocollection (id)
# );

class videocollectionmembership:
    def __init__(self, videoid, collectionid):
        self.videoid = videoid
        self.collectionid = collectionid


# Fetches videocollectionmembership object from the database by videoid or collectionid.
# If 'VIDEO' is specified as argument, it fetches all collections that the video is part of.
# If 'COLLECTION' is specified as argument, it fetches all videos that the collection has.
# Returns a videocollectionmembership object list if the operation is carried out succesfully, None if not.
def getvideocollectionmembershipbyid(id, type="VIDEO"):
    db = get_db()
    objectlist = []

    match type:
        case "VIDEO":
            try:
                result = db.execute(
                    'SELECT * FROM videocollectionmembership WHERE videocollectionmembership.videoid = ' + str(id)
                ).fetchall()
            except db.Error as db_error:
                print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
                print("{}".format(db_error))

            # Create the video object list
            for record in result:
                collectionrecord = collectionmodel.getvideocollectionbyid(record['collectionid'])
                objectlist.append(collectionrecord)
        case "COLLECTION":
            try:
                result = db.execute(
                    'SELECT * FROM videocollectionmembership WHERE videocollectionmembership.collectionid = ' + str(id)
                ).fetchall()
            except db.Error as db_error:
                print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
                print("{}".format(db_error))

            # Create the collection object list
            for record in result:
                videorecord = videomodel.getvideobyid(record['videoid'])
                objectlist.append(videorecord)

    return objectlist


# For specified video id, returns a list of collection objects that the video isn't in
def getinversedvideocollectionmembershipbyid(videoid):
    db = get_db()
    objectlist = []

    try:
        result = db.execute(
            "SELECT id FROM videocollection WHERE id NOT IN (SELECT collectionid FROM videocollectionmembership WHERE videocollectionmembership.videoid == ?)",
            (videoid,),
        ).fetchall()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))

    # Create the video object list
    for record in result:
        collectionrecord = collectionmodel.getvideocollectionbyid(record['id'])
        objectlist.append(collectionrecord)
    return objectlist


# DEPRECATED, USE VIDEOMODEL.addvideotocollection
# TODO: REMOVE OTHER USES OF THIS FUNCTION
# TODO: Insert videocollectionmembership info update logic Inserts videocollectionmembership objects into the
#  database. Accepts videoid and collectionid object as argument, returns videocollectionmembership id if operation
#  is carried out succesfully, None if not.
def createvideocollectionmembershipentry(videoid, collectionid):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT OR IGNORE INTO videocollectionmembership (videoid, collectionid) VALUES (?, ?)",
            (videoid, collectionid),
        )
        db.commit()
    except db.IntegrityError as db_error:  # This should only be called only if shorturl already exists.
        print(bcolors.WARNING + "Video collection already exists. Ignoring." + bcolors.ENDC)
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
    else:
        return cursor.lastrowid
    return None


# Remove entry with specified videoid and collectionid. Returns message status of the operation.
def removevideocollectionmembershipentry(videoid, collectionid):
    db = get_db()

    try:
        db.execute(
            "DELETE FROM videocollectionmembership WHERE videoid = ? AND collectionid = ?",
            (videoid, collectionid),
        )
        db.commit()
    except db.IntegrityError as db_error:
        print(bcolors.WARNING + "Video not part of collection. Ignoring." + bcolors.ENDC)
        return "Video not part of collection. Ignoring."
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return "Database error. Check console for details."
    return "Video removed from collection."


# Removes all entries of the specified collection id. Returns message if completed,
# prints error and returns None if not.
def removeallcollectionentries(collectionid):
    db = get_db()

    try:
        db.execute(
            "DELETE FROM videocollectionmembership WHERE collectionid = ?",
            (collectionid,),
        )
        db.commit()
    except db.IntegrityError as db_error:
        print(bcolors.WARNING + "Video not part of collection. Ignoring." + bcolors.ENDC)
        return None
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    return "Collection removed from relation table."
