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


#TODO: Decouple dl function with playlist function? Or maybe keep it as it is to avoid doing the job for yt-dlp which will download playlists better anyway
    #'title': 'recipes', 'playlist_count': 8, '_type': 'playlist', 'entries': [{'id': 'J305fi3nZ68', 'title':...}]
    #'_type' will be 'video' for single videos
@bp.cli.command("dl")
@click.argument("link")
def dl(link):

    locdict = {
        'home' : os.getcwd() + '\\videos\\'
    }
    output_template_dic = {
        'default' : "%(id)s.%(ext)s"
    }
    ytdlp_options = {'paths' : locdict, 'outtmpl' : output_template_dic, 'format': 'mp4'}

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
                    registervideo(subdct, locdict)
                except KeyError as keyerror:
                    print(bcolors.WARNING + "Problem adding video." + bcolors.ENDC)
                    print("{}".format(keyerror))

            case 'playlist': #playlist
                keys = ['id', 'title', 'playlist_count', '_type', 'entries']
                try:
                    subdct = {key: dict_dump[key] for key in keys}
                    ydl.download(link)
                    collectiontitle = None

                    #Create collection from playlist
                    try:
                        collectiontitle = subdct['title']
                        createcollection(collectiontitle, subdct['id'])
                    except db.IntegrityError as db_error:
                        print(bcolors.WARNING + "Problem creating collection. Perhaps it already exists? Videos will be added." + bcolors.ENDC)
                        print("{}".format(db_error))

                    #Try to register each video individually
                    for entry in subdct['entries']:
                        registervideo(entry, locdict, collectiontitle)
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
            "INSERT INTO video (shorturl, loc, downloaded, title, width, height, descr, resolution) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (dict['id'], loc, 1, dict['title'], dict['width'], dict['height'], dict['description'], dict['resolution']),
        )
        db.commit()
    except db.IntegrityError as db_error:
        print(bcolors.WARNING + "Problem adding video. Has the video already been downloaded?" + bcolors.ENDC)
        print("{}".format(db_error))
    else:
        addvideotocollection(cursor.lastrowid, 1) #TODO: Remove "All Videos" category hardcode?
        if collection_destination != None:
            pass #FIND collection id by title
                #THEN add

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
        print(bcolors.OKGREEN + "Added video to \"All Videos\" category" + bcolors.ENDC)

#TODO: FINISH AUTOMATIC PLAYLIST DL AS A SEPARATE FUNCTION?
def createcollection(name = "", shorturl = None):
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO videocollection (vcname, shorturl) VALUES (?,?)",
            (name, shorturl),
        )
        db.commit()
    except db.IntegrityError as db_error:
        print("{}".format(db_error))
    else:
        print(bcolors.OKGREEN + "Collection created." + bcolors.ENDC)
        pass