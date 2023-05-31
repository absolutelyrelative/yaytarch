import os

import click
from flask import (
    Blueprint, render_template, send_from_directory
)
from yt_dlp import YoutubeDL

from .db import get_db
from .model import collectionmodel
from .model import videomodel
from .tools import bcolors

# This blueprint takes care of the video view page and any future feature of it

bp = Blueprint('videos', __name__)


@bp.route('/video/<int:videoid>')
def viewvideo(videoid):
    video = videomodel.getvideobyid(videoid)

    return render_template('videoplay.html', video=video)


@bp.route("/video/source/<int:videoid>")
def load_video(videoid):
    video = videomodel.getvideobyid(videoid)

    file_name = os.path.basename(video.loc)
    dir_name = os.path.dirname(video.loc)

    return send_from_directory(dir_name, file_name)


# TODO: If this works, merge with load_video to save half the IO calls.
@bp.route("/video/source/thumb/<int:videoid>")
def load_picture(videoid):
    video = videomodel.getvideobyid(videoid)

    videolocation = video.loc
    videoshorturl = video.shorturl

    # TODO: Check if the file even exists, and cycle through formats. This is just to test.
    imagename = videoshorturl + ".webp"
    dirname = os.path.dirname(videolocation)

    return send_from_directory(dirname, imagename)


# DEPRECATED
# Gets video or playlist by link, automatically generates collection for playlists, and adds videos to respective collections
# 'title': 'recipes', 'playlist_count': 8, '_type': 'playlist', 'entries': [{'id': 'J305fi3nZ68', 'title':...}]
# '_type' will be 'video' for single videos
@bp.cli.command("dl")
@click.argument("link")
def dl(link):
    db = get_db()

    pathdicts = {
        'locdict': {
            'home': os.getcwd() + '\\videos\\'
        },
        'outputtemplatedict': {
            'default': "%(id)s.%(ext)s"
        }
    }

    # There is no way to specify thumbnail format in embedded mode to my knowledge, and 'write_all_thumbnails' : output_template_dic is too redundant.
    ytdlp_options = {'paths': pathdicts['locdict'], 'outtmpl': pathdicts['outputtemplatedict'], 'format': 'mp4',
                     'writethumbnail': True}

    with YoutubeDL(ytdlp_options) as ydl:
        print(bcolors.OKCYAN + "Downloading and parsing information...\n" + bcolors.ENDC)
        info = ydl.extract_info(link, download=False)
        dict_dump = ydl.sanitize_info(info)

        print(bcolors.OKCYAN + "Downloading videos...\n" + bcolors.ENDC)
        # Get video type
        match dict_dump['_type']:
            case 'video':  # single video
                keys = ['id', 'title', 'thumbnail', 'description', 'format', 'format_id', 'ext', 'width', 'height',
                        'resolution']
                try:
                    subdct = {key: dict_dump[key] for key in keys}
                    ydl.download(link)
                    registervideo(subdct, pathdicts['locdict'])
                except KeyError as keyerror:
                    print(bcolors.WARNING + "Problem adding video." + bcolors.ENDC)
                    print("{}".format(keyerror))

            case 'playlist':  # playlist
                keys = ['id', 'title', 'playlist_count', '_type', 'entries']
                try:
                    subdct = {key: dict_dump[key] for key in keys}
                    ydl.download(link)
                    collectiontitle = subdct['title']

                    if collectionmodel.findcollectionbyname(collectiontitle) == None:
                        print(bcolors.OKCYAN + "Collection doesn't exist. Creating...\n" + bcolors.ENDC)
                        newcollection = collectionmodel.videocollection(0, collectiontitle, subdct['id'])
                        collectionmodel.createvideocollectionentry(newcollection)
                    else:
                        print(bcolors.OKCYAN + "Collection already exists. Appending video to it...\n" + bcolors.ENDC)
                    # Try to register each video individually
                    for entry in subdct['entries']:
                        registervideo(entry, pathdicts['locdict'], collectiontitle)
                except KeyError as keyerror:
                    print(bcolors.WARNING + "Problem adding video." + bcolors.ENDC)
                    print("{}".format(keyerror))
            case _:  # may be required for other platforms
                pass


# Creates Video entry and registers to specified collection
def registervideo(dict, locdict, collection_destination=None):
    loc = locdict['home'] + dict['id'] + '.' + dict['ext']

    # Create video object
    videoobject = videomodel.video(0, dict['id'], dict['title'], dict['width'], dict['height'], loc,
                                   dict['description'], dict['resolution'], 1)
    videoobjecttoupdate = videomodel.getvideobyshorturl(dict['id'])  # Check if video object already exists
    if videoobjecttoupdate is None:  # If video object is new, create it
        print("Doesn't exist")
        newvideoid = videomodel.createvideoentry(videoobject)
    else:  # If it's not new, update it
        print("Exists")  # TODO: Insert update logic function call here
        newvideoid = videoobjecttoupdate.id

    # Add the new video to collections
    print(bcolors.OKCYAN + "Adding video to collection " + bcolors.BOLD + "All videos" + bcolors.ENDC, end=': ')
    videomodel.addvideotocollection(newvideoid, collectionmodel.findcollectionbyname("All videos").id)

    if collection_destination != None:
        print(bcolors.OKCYAN + "Adding video to collection " + bcolors.BOLD + collection_destination + bcolors.ENDC,
              end=': ')
        newrecordid = videomodel.addvideotocollection(newvideoid,
                                                      collectionmodel.findcollectionbyname(collection_destination).id)
