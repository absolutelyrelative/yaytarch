import os
from yt_dlp import YoutubeDL

from model import videocollectionrelmodel
from db import get_db
from model import collectionmodel
from model import videomodel
from tools.config import *


# Gets video or playlist by link, automatically generates collection for playlists, and adds videos to
# respective collections
# 'title': 'recipes', 'playlist_count': 8, '_type': 'playlist', 'entries': [{'id':
# 'J305fi3nZ68', 'title':...}] '_type' will be 'video' for single videos
def dl(link, collection_destination = None):
    db = get_db()
    opts = DlOptions

    with YoutubeDL(opts.ytdlp_options) as ydl:
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
                    registervideo(subdct, opts.pathdicts['locdict'], collection_destination)
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
                        registervideo(entry, opts.pathdicts['locdict'], collectiontitle)
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
