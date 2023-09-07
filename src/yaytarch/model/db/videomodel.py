# This module provides a class object for videos and helper methods to fetch and insert videos. Any data coherence
# check should be done here.
from ...db import get_db
from ...tools.outputformat import bcolors


class video:

    # Consider using **kwargs, not a very pretty solution :(
    def __init__(self, id, shorturl, title, description, uploader_url, view_count, webpage_url, like_count,
                 availability, duration_string, ext, width, height, upload_date, channel, epoch, thumbnail,
                 jsonloc, loc):
        self.id = id
        self.shorturl = shorturl
        self.title = title
        self.description = description
        self.uploader_url = uploader_url
        self.view_count = view_count
        self.webpage_url = webpage_url
        self.like_count = like_count
        self.availability = availability
        self.duration_string = duration_string
        self.ext = ext
        self.width = width
        self.height = height
        self.upload_date = upload_date
        self.channel = channel
        self.epoch = epoch
        # Custom fields:
        self.thumbnail = thumbnail
        self.jsonloc = jsonloc
        self.loc = loc


# Because the amount of arguments is large, I'm using a helper function to get the result into a neat object.
def parseresultintoobject(result):
    videoobject = video(result['id'], result['shorturl'], result['title'], result['description'],
                        result['uploader_url'], result['view_count'], result['webpage_url'], result['like_count'],
                        result['availability'], result['duration_string'], result['ext'], result['width'],
                        result['height'], result['upload_date'], result['channel'], result['epoch'],
                        result['thumbnail'], result['jsonloc'], result['loc'])

    return videoobject


# Gets all videos in a list
def getallvideos():
    db = get_db()

    try:
        result = db.execute('SELECT * FROM video WHERE shorturl IS NOT NULL'
                            ).fetchall()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    if result is not None:
        videolist = []
        for entry in result:
            videolist.append(parseresultintoobject(entry))
        return videolist
    return None


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
    if result is not None:
        videoobject = parseresultintoobject(result)
        return videoobject
    return None


# TODO: Insert video info update logic
# TODO: If video is already downloaded (UNIQUE constraint failed: video.loc) but
#  not added to database, this will be a problem. Fix it. Inserts video objects into the database. Accepts video
#  object as argument, returns video id if operation is carried out succesfully, None if not.
def createvideoentry(video):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT OR IGNORE INTO video (shorturl, title, description, uploader_url, view_count, webpage_url, like_count, availability, duration_string, ext, width, height, upload_date, channel, epoch, thumbnail,jsonloc, loc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (video.shorturl, video.title, video.description, video.uploader_url, video.view_count, video.webpage_url,
             video.like_count, video.availability, video.duration_string, video.ext, video.width, video.height,
             video.upload_date, video.channel, video.epoch, video.thumbnail, video.jsonloc, video.loc),
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
        videoobject = parseresultintoobject(result)
        return videoobject
    return None


# This function takes in an old video object and a new video object and updates it in the database
def updatevideoentry(oldvideo: video, newvideo: video):
    db = get_db()

    try:
        result = db.execute(
            "UPDATE video SET title = ?, description = ?, uploader_url = ?, view_count = ?, webpage_url = ?, like_count = ?, availability = ?, duration_string = ?, ext = ?, width = ?, height = ?, upload_date = ?, channel = ?, epoch = ?, thumbnail = ?, jsonloc = ?, loc = ? WHERE id == ?;",
            (newvideo.title, newvideo.description, newvideo.uploader_url,
             newvideo.view_count, newvideo.webpage_url, newvideo.like_count,
             newvideo.availability, newvideo.duration_string, newvideo.ext,
             newvideo.width, newvideo.height, newvideo.upload_date,
             newvideo.channel, newvideo.epoch, newvideo.thumbnail,
             newvideo.jsonloc, newvideo.loc, oldvideo.id), )

        db.commit()
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    except db.IntegrityError as db_error:
        print("{}".format(db_error))
    if result is not None:
        print(bcolors.OKGREEN + "Video entry updated." + bcolors.ENDC)
        return result
    return None
