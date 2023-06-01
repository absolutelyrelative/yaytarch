# This module provides a class object for videocollection and helper methods to fetch and insert video collections.
# Any data coherence check should be done here.
from ..db import get_db
from tools.outputformat import bcolors


# CREATE TABLE videocollection (
#    id INTEGER PRIMARY KEY AUTOINCREMENT,
#    vcname TEXT UNIQUE NOT NULL,
#    shorturl TEXT DEFAULT ""
#    --Collections are treated locally to nullify same video redownload, therefore shorturl can be null
# );

class videocollection:
    def __init__(self, id, vcname, shorturl):
        self.id = id
        self.vcname = vcname
        self.shorturl = shorturl


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
    videocollectionobject = videocollection(result['id'], result['vcname'], result['shorturl'])

    return videocollectionobject


def findcollectionbyname(name):
    db = get_db()
    try:
        result = db.execute("SELECT * FROM videocollection WHERE videocollection.vcname = '" + name + "'"
                            ).fetchone()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    # print(result['iddsftfyuihklkòlàçdfsxzazzzzzzzzzzzzzzzzzzzzz cazzo porco diooooooooooooooo do pioruna!!! curva mac iunih ouyvytf'])
    if result is not None:
        videocollectionobject = videocollection(result['id'], result['vcname'], result['shorturl'])
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
            "INSERT OR IGNORE INTO videocollection (vcname, shorturl) VALUES (?, ?)",
            (videocollection.vcname, videocollection.shorturl),
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
