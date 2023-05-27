import functools, click
from yt_dlp import YoutubeDL
from .tools import bcolors

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)

from yaytarch.db import get_db
import os

#This blueprint takes care of the video view page and any future feature of it

bp = Blueprint('videos', __name__)

@bp.route('/video/<int:video_id>')
def viewvideo(video_id):
    db = get_db()

    videos = db.execute('SELECT * FROM video WHERE video.id = ' + str(video_id)
    ).fetchall()

    return render_template('videoplay.html', videos = videos)

@bp.route("/video/source/<int:video_id>")
def load_video(video_id):
    db = get_db()
    video = db.execute('SELECT loc FROM video WHERE video.id = ' + str(video_id)
    ).fetchone()
    location_from_db = video['loc']

    file_name = os.path.basename(location_from_db)
    dir_name = os.path.dirname(location_from_db)

    return send_from_directory(dir_name, file_name)

#TODO: If this works, merge with load_video to save half the IO calls.
@bp.route("/video/source/thumb/<int:video_id>")
def load_picture(video_id):
    db = get_db()
    video = db.execute('SELECT shorturl, loc FROM video WHERE video.id = ' + str(video_id)
    ).fetchone()

    videolocation = video['loc']
    videoshorturl = video['shorturl']

    #TODO: Check if the file even exists, and cycle through formats. This is just to test.
    imagename = videoshorturl + ".webp"
    dirname = os.path.dirname(videolocation)

    return send_from_directory(dirname, imagename)




#Gets video or playlist by link, automatically generates collection for playlists, and adds videos to respective collections
    #'title': 'recipes', 'playlist_count': 8, '_type': 'playlist', 'entries': [{'id': 'J305fi3nZ68', 'title':...}]
    #'_type' will be 'video' for single videos
@bp.cli.command("dl")
@click.argument("link")
def dl(link):
    db = get_db()

    pathdicts = {
        'locdict' : {
            'home' : os.getcwd() + '\\videos\\'
        },
        'outputtemplatedict' : {
            'default' : "%(id)s.%(ext)s"
        }
    }
    
    #There is no way to specify thumbnail format in embedded mode to my knowledge, and 'write_all_thumbnails' : output_template_dic is too redundant.
    ytdlp_options = {'paths' : pathdicts['locdict'], 'outtmpl' : pathdicts['outputtemplatedict'], 'format': 'mp4', 'writethumbnail' : True}

    with YoutubeDL(ytdlp_options) as ydl:
        info = ydl.extract_info(link, download=False)
        dict_dump = ydl.sanitize_info(info)

        #Get video type
        match dict_dump['_type']:
            case 'video': #single video
                keys = ['id', 'title', 'thumbnail', 'description', 'format', 'format_id', 'ext', 'width', 'height', 'resolution']
                try:
                    subdct = {key: dict_dump[key] for key in keys}
                    ydl.download(link)
                    registervideo(subdct, pathdicts['locdict'])
                except KeyError as keyerror:
                    print(bcolors.WARNING + "Problem adding video." + bcolors.ENDC)
                    print("{}".format(keyerror))

            case 'playlist': #playlist
                keys = ['id', 'title', 'playlist_count', '_type', 'entries']
                try:
                    subdct = {key: dict_dump[key] for key in keys}
                    ydl.download(link)
                    collectiontitle = subdct['title']
                    
                    if findcollectionid(collectiontitle) == None:
                        createcollection(collectiontitle, subdct['id'])
                    else:
                        print("Collection already exists. Appending video to it.")
                    #Try to register each video individually
                    for entry in subdct['entries']:
                        registervideo(entry, pathdicts['locdict'], collectiontitle)
                except KeyError as keyerror:
                    print(bcolors.WARNING + "Problem adding video." + bcolors.ENDC)
                    print("{}".format(keyerror))
            case _: #may be required for other platforms
                pass

#Creates Video entry and registers to specified collection
#TODO: ADD "collection destination" function parameter to call if specified
def registervideo(dict, locdict, collection_destination = None):
    db = get_db()
    cursor = db.cursor()
    loc = locdict['home'] + dict['id'] + '.' + dict['ext']
    print('location: ' + loc)

    try:
        cursor.execute(
            "INSERT OR IGNORE INTO video (shorturl, loc, downloaded, title, width, height, descr, resolution) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (dict['id'], loc, 1, dict['title'], dict['width'], dict['height'], dict['description'], dict['resolution']),
        )
        db.commit()
    except db.IntegrityError as db_error: #This will rarely be called because of the IGNORE SQL statement.
        print(bcolors.WARNING + "Problem adding video. Has the video already been downloaded? Carrying on..." + bcolors.ENDC)
        print("{}".format(db_error))
    else:
        print("Adding video to collection \"All videos\"")
        addvideotocollection(cursor.lastrowid, findcollectionid("All videos")) #TODO: Remove "All Videos" category hardcode?
        if collection_destination != None:
            print("Adding video to collection " + collection_destination)
            addvideotocollection(cursor.lastrowid, findcollectionid(collection_destination))

#Assigns a video to a collection
def addvideotocollection(video_id, collection_id):
    db = get_db()

    try:
        db.execute(
            "INSERT INTO videocollectionmembership (videoid, collectionid) VALUES (?, ?)",
            (video_id,collection_id),
        )
        db.commit()
    except db.IntegrityError as db_error:
        print("{}".format(db_error))
    else:
        print(bcolors.OKGREEN + "Done." + bcolors.ENDC)

#Creates a collection with a given name
def createcollection(name = "", shorturl = None):
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO videocollection (vcname, shorturl) VALUES (?,?)",
            (name, shorturl),
        )
        db.commit()
    except db.IntegrityError as db_error: #This will rarely be called because of the IGNORE SQL statement.
        print("{}".format(db_error))
    else:
        print(bcolors.OKGREEN + "Collection created." + bcolors.ENDC)

#This method finds a collection id by name. Maybe Names should be the key.
def findcollectionid(name):
    db = get_db()

    collection = db.execute('SELECT id FROM videocollection WHERE videocollection.vcname = \'' + name + '\''
    ).fetchone()

    if collection == None:
        return None
    else:
        return collection['id']