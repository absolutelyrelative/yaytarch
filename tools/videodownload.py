import os
from yt_dlp import YoutubeDL

from model import videocollectionrelmodel
from db import get_db
from model import collectionmodel
from model import videomodel
from tools.config import *
import json


# Gets video or playlist by link, automatically generates collection for playlists, and adds videos to
# respective collections
def dl(link, collection_destination=None):
    db = get_db()
    opts = DlOptions

    with YoutubeDL(DlOptions.ytdlp_options) as ydl:
        print(bcolors.OKCYAN + "Downloading & parsing information...\n" + bcolors.ENDC)
        info = ydl.extract_info(link, download=False)
        dictdump = ydl.sanitize_info(info)

        print(bcolors.OKCYAN + "Downloading videos...\n" + bcolors.ENDC)
        # Get video type
        match dictdump['_type']:
            case 'video':  # single video
                try:
                    # Cycle through keys
                    subdct = {key: dictdump[key] for key in DlArguments.videokeys}

                    # Download the video
                    ydl.download(link)
                    registervideo(subdct, opts.pathdicts['locdict'], collection_destination)
                except KeyError as keyerror:
                    print(bcolors.WARNING + "Problem adding video." + bcolors.ENDC)
                    print("{}".format(keyerror))

            # PROBLEM! ONLY this is called when playlists are found, it doesn't cycle through.
            case 'playlist':  # playlist
                try:
                    # Cycle through keys
                    playlistsubdct = {key: dictdump[key] for key in DlArguments.playlistkeys}
                    thumbnailssubdct = dictdump['thumbnails']

                    # Extract downloaded thumbnail location
                    thumbnailloc = ""  # Just in case no thumbnail has been downloaded
                    for thumbnail in thumbnailssubdct:
                        if "filepath" in thumbnail:
                            thumbnailloc = thumbnail["filepath"]

                    # Download the playlist
                    ydl.download(link)
                    collectiontitle = playlistsubdct['title']

                    # Save to JSon file
                    locdict = opts.pathdicts['locdict']
                    jsonloc = locdict['home'] + playlistsubdct['id'] + '.json'
                    with open(jsonloc, 'w') as outfile:
                        json.dump(playlistsubdct, outfile, indent='\t')

                    if collectionmodel.findcollectionbyname(collectiontitle) == None:
                        print(bcolors.OKCYAN + "Collection doesn't exist. Creating...\n" + bcolors.ENDC)
                        # Wow I really wish I used **Kwargs now
                        # TODO: Add json and thumb loc
                        newcollection = collectionmodel.videocollection(0, playlistsubdct['id'],
                                                                        playlistsubdct['title'],
                                                                        playlistsubdct['availability'],
                                                                        playlistsubdct['modified_date'],
                                                                        playlistsubdct['playlist_count'],
                                                                        playlistsubdct['uploader_url'],
                                                                        playlistsubdct['epoch'], thumbnailloc,
                                                                        jsonloc)
                        newcollectionid = collectionmodel.createvideocollectionentry(newcollection)
                        if newcollectionid is None:
                            raise Exception("Could not create video collection entry.")
                    else:
                        print(bcolors.OKCYAN + "Collection already exists. Appending videos to it...\n" + bcolors.ENDC)
                    # Try to register each video individually
                    # Because of course the video entries in the playlist info don't share the same keys.
                    for entry in playlistsubdct['entries']:
                        # Redownload information
                        info = ydl.extract_info(entry['id'], download=False)
                        dictdump = ydl.sanitize_info(info)
                        subdct = {key: dictdump[key] for key in DlArguments.videokeys}
                        # Save to JSon
                        infojson = json.dumps(subdct, indent='\t')

                        registervideo(subdct, opts.pathdicts['locdict'], collectiontitle)

                    # Save to JSon
                    infojson = json.dumps(subdct, indent='\t')
                except KeyError as keyerror:
                    print(bcolors.WARNING + "Problem adding video." + bcolors.ENDC)
                    print("{}".format(keyerror))
            case _:  # may be required for other platforms
                pass


# Creates Video entry and registers to specified collection
def registervideo(dict, locdict, collection_destination=None):
    loc = locdict['home'] + dict['id'] + '.' + dict['ext']

    # TODO: Generate a better one for pictures. Playlists already have file location saved in json, videos don't? :(
    thumbloc = locdict['home'] + dict['id'] + '.jpg'
    jsonloc = locdict['home'] + dict['id'] + '.json'

    # Save to JSon file
    with open(jsonloc, 'w') as outfile:
        json.dump(dict, outfile, indent='\t')

    # Create video object
    videoobject = videomodel.video(0, dict['id'], dict['title'], dict['description'],
                                   dict['uploader_url'], dict['view_count'], dict['webpage_url'], dict['like_count'],
                                   dict['availability'], dict['duration_string'], dict['ext'], dict['width'],
                                   dict['height'], dict['upload_date'], dict['channel'], dict['epoch'],
                                   thumbloc, jsonloc, loc)

    videoobjecttoupdate = videomodel.getvideobyshorturl(dict['id'])  # Check if video object already exists
    if videoobjecttoupdate is None:  # If video object is new, create it
        print("Creating video entry.")
        newvideoid = videomodel.createvideoentry(videoobject)
        if newvideoid is None:
            raise Exception("newvideoid returned None when it was already assured that it wouldn't.")
    else:  # If it's not new, update it
        print("Video entry already exists.")  # TODO: Insert update logic function call here
        newvideoid = videoobjecttoupdate.id

    # Add the new video to collections
    print(bcolors.OKCYAN + "Adding video to collection " + bcolors.BOLD + "All videos" + bcolors.ENDC, end=': ')
    videomodel.addvideotocollection(newvideoid, collectionmodel.findcollectionbyname("All videos").id)

    if collection_destination != None:
        print(bcolors.OKCYAN + "Adding video to collection " + bcolors.BOLD + collection_destination + bcolors.ENDC,
              end=': ')
        newrecordid = videomodel.addvideotocollection(newvideoid,
                                                      collectionmodel.findcollectionbyname(collection_destination).id)
