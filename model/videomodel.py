# This module provides a class object for videos and helper methods to fetch and insert videos. Any data coherence
# check should be done here.
from ..db import get_db
from tools.outputformat import bcolors


# """ CREATE TABLE video (
#    id INTEGER PRIMARY KEY AUTOINCREMENT,
#    shorturl TEXT UNIQUE NOT NULL,
#    title TEXT DEFAULT "",
#    width INT DEFAULT 320,
#    height INT DEFAULT 240,
#    loc TEXT UNIQUE NOT NULL,
#    descr TEXT DEFAULT "",
#    resolution TEXT DEFAULT "",
#    downloaded BOOLEAN DEFAULT 0
# ); """

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


# Fetches video object from the database. Returns a video object if the operation is carried out succesfully,
# None if not.
def getvideobyid(videoid):
    db = get_db()

    try:
        result = db.execute('SELECT * FROM video WHERE video.id = ' + str(videoid)
                            ).fetchone()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    videoobject = video(result['id'], result['shorturl'], result['title'], result['width'], result['height'],
                        result['loc'],
                        result['descr'], result['resolution'], result['downloaded'])

    return videoobject


# TODO: Insert video info update logic
# TODO: If video is already downloaded (UNIQUE constraint failed: video.loc) but
#  not added to database, this will be a problem. Fix it. Inserts video objects into the database. Accepts video
#  object as argument, returns video id if operation is carried out succesfully, None if not.
def createvideoentry(video):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT OR IGNORE INTO video (shorturl, loc, downloaded, title, width, height, descr, resolution) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (video.shorturl, video.loc, video.downloaded, video.title, video.width, video.height, video.descr,
             video.resolution),
        )
        db.commit()
    except db.IntegrityError as db_error:  # This should only be called only if shorturl already exists.
        print("{}".format(db_error))
        print(bcolors.WARNING + "Video already exists. Attempting to update database." + bcolors.ENDC)
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
    else:
        return cursor.lastrowid
    return None


# Assigns a video to a collection. Accepts video id as argument, returns videocollectionmembership id if operation is
# carried out succesfully, None if not.
def addvideotocollection(videoid, collectionid):
    db = get_db()
    cursor = db.cursor()

    if checkcollectionmembership(videoid, collectionid) is None:  # New video in the collection
        try:
            db.execute(
                "INSERT INTO videocollectionmembership (videoid, collectionid) VALUES ({0}, {1})".format(
                    str(videoid), str(collectionid))
            )
            db.commit()
        except db.Error as db_error:
            print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
            print("{}".format(db_error))
        else:
            print(bcolors.OKGREEN + "Done." + bcolors.ENDC)
            return db.total_changes  # Kind of useless for now
        return None
    else:
        print(bcolors.WARNING + "Video already part of collection. Ignoring." + bcolors.ENDC)
        return None


# I found no neat way in SQLite to check membership with nested selects.
# Consider the following approach :
# INSERT INTO videocollectionmembership (videoid)
# 	SELECT videoid
# 	 FROM (
# 			SELECT 25 AS videoid
# 			) AS o
# 	WHERE NOT EXISTS (
# 						SELECT *
# 						FROM videocollectionmembership
# 						WHERE videoid == o.videoid
# 						);
def checkcollectionmembership(videoid, collectionid):
    db = get_db()

    try:
        result = db.execute("SELECT * FROM videocollectionmembership  WHERE videoid = '" + str(videoid) + "'"
                                                                                                          "                                         AND collectionid = '" + str(
            collectionid) + "'"
                            ).fetchone()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    return result


def getvideobyshorturl(shorturl):
    db = get_db()

    try:
        result = db.execute("SELECT * FROM video WHERE video.shorturl = '" + shorturl + "'"
                            ).fetchone()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    if result is not None:
        videoobject = video(result['id'], result['shorturl'], result['title'], result['width'], result['height'],
                            result['loc'],
                            result['descr'], result['resolution'], result['downloaded'])
        return videoobject
    return None
