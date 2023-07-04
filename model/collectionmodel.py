# This module provides a class object for videocollection and helper methods to fetch and insert video collections.
# Any data coherence check should be done here.
from db import get_db
from tools.outputformat import bcolors


class videocollection:
    def __init__(self, id, shorturl, title, availability, modified_date, playlist_count, uploader_url, epoch,
                 thumbnail, jsonloc):
        self.id = id
        self.shorturl = shorturl
        self.title = title
        self.availability = availability
        self.modified_date = modified_date
        self.playlist_count = playlist_count
        self.uploader_url = uploader_url
        self.epoch = epoch

        self.thumbnail = thumbnail
        self.jsonloc = jsonloc


# Fetches videocollection object from the database. Returns a videocollection object if the operation is carried out
# succesfully, None if not.
def getvideocollectionbyid(videocollectionid):
    db = get_db()

    try:
        result = db.execute("SELECT * FROM videocollection WHERE videocollection.id = " + str(videocollectionid)
                            ).fetchone()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    videocollectionobject = videocollection(result['id'], result['shorturl'], result['title'], result['availability'],
                                            result['modified_date'], result['playlist_count'], result['uploader_url'],
                                            result['epoch'], result['thumbnail'], result['jsonloc'])

    return videocollectionobject


def findcollectionbyname(name):
    db = get_db()
    try:
        result = db.execute("SELECT * FROM videocollection WHERE videocollection.title = '" + name + "'"
                            ).fetchone()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    # print(result['iddsftfyuihklkòlàçdfsxzazzzzzzzzzzzzzzzzzzzzz cazzo porco diooooooooooooooo do pioruna!!! curva mac iunih ouyvytf'])
    if result is not None:
        videocollectionobject = videocollection(result['id'], result['shorturl'], result['title'],
                                                result['availability'],
                                                result['modified_date'], result['playlist_count'],
                                                result['uploader_url'],
                                                result['epoch'], result['thumbnail'], result['jsonloc'])
        return videocollectionobject
    else:
        return None


# TODO: Insert videocollection info update logic Inserts videocollection objects into the database. Accepts
#  videocollection object as argument, returns videocollection id if operation is carried out succesfully, None if not.
def createvideocollectionentry(videocollection):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT OR IGNORE INTO videocollection (shorturl, title, availability, modified_date, playlist_count, uploader_url, epoch, thumbnail, jsonloc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (videocollection.shorturl, videocollection.title, videocollection.availability,
             videocollection.modified_date, videocollection.playlist_count, videocollection.uploader_url,
             videocollection.epoch, videocollection.thumbnail, videocollection.jsonloc),
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


# Gets all collections as list to generate collection html
def getallcollections():
    db = get_db()
    objectlist = []

    try:
        result = db.execute('SELECT * FROM videocollection'
                            ).fetchall()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))

    # Create the video object list
    for record in result:
        collectionrecord = getvideocollectionbyid(record['id'])
        objectlist.append(collectionrecord)

    return objectlist


# Removes collection from specified id. Returns message if completed,
# prints error and returns None if not.
def removecollection(collectionid):
    db = get_db()

    try:
        db.execute(
            "DELETE FROM videocollection WHERE id = ?",
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
    return "Collection has been deleted."
