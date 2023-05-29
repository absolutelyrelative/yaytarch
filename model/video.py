#This module provides a class object for videos and helper methods to fetch and insert videos. Any data coherence check should be done here.
from yaytarch.db import get_db
from . import collection as collectionmodel
from . import videocollectionmembership as videocollectionmembershipmodel
from yaytarch.tools import bcolors

""" CREATE TABLE video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shorturl TEXT UNIQUE NOT NULL,
    title TEXT DEFAULT "",
    width INT DEFAULT 320,
    height INT DEFAULT 240,
    loc TEXT UNIQUE NOT NULL,
    descr TEXT DEFAULT "",
    resolution TEXT DEFAULT "",
    downloaded BOOLEAN DEFAULT 0
); """

class video:
    def __init__(self, id, shorturl, title, width, height, loc, descr, resolution, downloaded):
        self.id = id
        self.shorturl = shorturl
        self.title = title
        self.width = width
        self.height = height
        self.loc = loc
        self.descr = descr
        self.resolution = resolution
        self.downloaded = downloaded

#Fetches video object from the database. Returns a video object if the operation is carried out succesfully, None if not.
def getvideobyid(videoid):
    db = get_db()

    try:
        result = db.execute('SELECT * FROM video WHERE video.id = ' + str(videoid)
        ).fetchone()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    videoobject = video(result['id'], result['shorturl'], result['title'], result['width'], result['height'], result['loc'],
                        result['descr'], result['resolution'], result['downloaded'])
    
    return videoobject

#TODO: Insert video info update logic
#TODO: If video is already downloaded (UNIQUE constraint failed: video.loc) but not added to database, this will be a problem. Fix it.
#Inserts video objects into the database. Accepts video object as argument, returns video id if operation is carried out succesfully, None if not.
def createvideoentry(video):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT OR IGNORE INTO video (shorturl, loc, downloaded, title, width, height, descr, resolution) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (video.shorturl, video.loc, video.downloaded, video.title, video.width, video.height, video.descr, video.resolution),
        )
        db.commit()
    except db.IntegrityError as db_error: #This should only be called only if shorturl already exists.
        print("{}".format(db_error))
        print(bcolors.WARNING + "Video already exists. Attempting to update database." + bcolors.ENDC)
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
    else:
        return cursor.lastrowid
    return None

#Assigns a video to a collection. Accepts video id as argument, returns videocollectionmembership id if operation is carried out succesfully, None if not.
def addvideotocollection(videoid, collectionid):
    db = get_db()
    cursor = db.cursor()

    try:
        db.execute(
            "INSERT OR IGNORE INTO videocollectionmembership (videoid, collectionid) VALUES (?, ?)",
            (videoid,collectionid),
        )
        db.commit()
    except db.IntegrityError as db_error: #This should only be called only if shorturl already exists.
        print(bcolors.WARNING + "Video already part of collection. Ignoring." + bcolors.ENDC)
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
    else:
        print(bcolors.OKGREEN + "Done." + bcolors.ENDC)
        return cursor.lastrowid
    return None

def getvideobyshorturl(shorturl):
    db = get_db()

    try:
        result = db.execute('SELECT * FROM video WHERE video.shorturl = ' + shorturl
        ).fetchone()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    videoobject = video(result['id'], result['shorturl'], result['title'], result['width'], result['height'], result['loc'],
                        result['descr'], result['resolution'], result['downloaded'])
    
    return videoobject