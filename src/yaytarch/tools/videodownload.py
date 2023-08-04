import json

from yt_dlp import YoutubeDL

from ..db import get_db
from ..model import collectionmodel
from ..model import videomodel
from .config import *


# Helper function to begin the download process by only specifying id. Useful for refreshing videos on the webpage.
def dlbyid(videoid: int):
    videoobjecttoupdate = videomodel.getvideobyid(videoid)
    if videoobjecttoupdate is None:
        print(
            bcolors.FAIL + "Couldn't find video by videoid. Please report this bug, it should never happen." + bcolors.ENDC)
    else:
        print(bcolors.OKCYAN + "Updating video " + bcolors.BOLD + videoobjecttoupdate.title + bcolors.ENDC)
        dl(videoobjecttoupdate.shorturl)


# Helper function to begin the download process by only specifying id. Useful for refreshing collections on the webpage.
def dlplaylistbyid(collectionid: int):
    collectionobjecttoupdate = collectionmodel.getvideocollectionbyid(collectionid)
    if collectionobjecttoupdate is None:
        print(
            bcolors.FAIL + "Couldn't find collection by collectionid. Please report this bug, it should never happen." + bcolors.ENDC)
    else:
        print(bcolors.OKCYAN + "Updating collection " + bcolors.BOLD + collectionobjecttoupdate.title + bcolors.ENDC)

        # Checking if collection is local
        if collectionobjecttoupdate.shorturl != "":
            dl(collectionobjecttoupdate.shorturl)
        else:
            print(
                bcolors.FAIL + "Couldn't update collection, it is a local collection with an unspecified url." + bcolors.ENDC)


# Gets video or playlist by link, automatically generates collection for playlists, and adds videos to
# respective collections
def dl(link, collection_destination=None):
    opts = DlOptions(None)

    with YoutubeDL(opts.ytdlp_options) as ydl:
        print(bcolors.OKCYAN + "Downloading & parsing information...\n" + bcolors.ENDC)
        info = ydl.extract_info(link, download=False)
        dictdump = ydl.sanitize_info(info)

        print(bcolors.OKCYAN + "Downloading videos...\n" + bcolors.ENDC)
        # Get video type
        match dictdump['_type']:
            case 'video':  # single video
                # Download the video
                ydl.download(link)
                # Process the video locally
                parsevideoinfo(dictdump, collection_destination)

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
                    jsonfilename = playlistsubdct['id'] + '.json'
                    jsonloc = os.path.join(opts.pathdicts['locdict']['home'], jsonfilename)

                    with open(jsonloc, 'w') as outfile:
                        json.dump(playlistsubdct, outfile, indent='\t')

                    # Uh, why EXACTLY was I checking by title and not by shorturl?
                    # TODO: Test change
                    oldcollection = collectionmodel.findcollectionbyshorturl(playlistsubdct['id'])
                    if oldcollection is None:
                        print(bcolors.OKCYAN + "Collection doesn't exist. Creating...\n" + bcolors.ENDC)
                        # Wow I really wish I used **Kwargs now
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
                        print(bcolors.OKCYAN + "Collection already exists. Updating videos...\n" + bcolors.ENDC)
                        # TODO: This is redundant, merge with the one above
                        newcollection = collectionmodel.videocollection(0, playlistsubdct['id'],
                                                                        playlistsubdct['title'],
                                                                        playlistsubdct['availability'],
                                                                        playlistsubdct['modified_date'],
                                                                        playlistsubdct['playlist_count'],
                                                                        playlistsubdct['uploader_url'],
                                                                        playlistsubdct['epoch'], thumbnailloc,
                                                                        jsonloc)
                        collectionmodel.updatecollectionentry(oldcollection,
                                                              newcollection)  # TODO: Test update function
                    # Try to register each video individually
                    # Because of course the video entries in the playlist info don't share the same keys.
                    for entry in playlistsubdct['entries']:
                        # Redownload information
                        info = ydl.extract_info(entry['id'], download=False)
                        dictdump = ydl.sanitize_info(info)

                        # Process the video locally
                        parsevideoinfo(dictdump, collectiontitle)
                except KeyError as keyerror:
                    print(bcolors.WARNING + "Problem adding video." + bcolors.ENDC)
                    print("{}".format(keyerror))
            case _:  # may be required for other platforms / channels
                pass


# Creates Video entry and registers to specified collection
def registervideo(video, collection_destination=None):
    # Check if video object already exists by shorturl
    videoobjecttoupdate = videomodel.getvideobyshorturl(video.shorturl)
    if videoobjecttoupdate is None:  # If video object is new, create it
        print("Creating video entry.")
        newvideoid = videomodel.createvideoentry(video)
        if newvideoid is None:
            raise Exception("newvideoid returned None when it was already assured that it wouldn't.")
    else:  # If it's not new, update it
        print(
            bcolors.OKCYAN + "Video entry already exists. Updating " + bcolors.BOLD + videoobjecttoupdate.title + bcolors.ENDC,
            end=': ')
        videomodel.updatevideoentry(videoobjecttoupdate, video)
        newvideoid = videoobjecttoupdate.id

    # Add the new video to collections
    print(bcolors.OKCYAN + "Adding video to collection " + bcolors.BOLD + "All videos" + bcolors.ENDC, end=': ')
    videomodel.addvideotocollection(newvideoid, collectionmodel.findcollectionbyname("All videos").id)

    if collection_destination is not None:
        print(bcolors.OKCYAN + "Adding video to collection " + bcolors.BOLD + collection_destination + bcolors.ENDC,
              end=': ')
        newrecordid = videomodel.addvideotocollection(newvideoid,
                                                      collectionmodel.findcollectionbyname(collection_destination).id)


# Helper function to configure videos for local use.

def parsevideoinfo(dictdump, collection_destination=None):
    opts = DlOptions(None)

    try:
        # Parse keys we need
        subdct = {key: dictdump[key] for key in DlArguments.videokeys}

        # Create the local video objects
        # set up file extensions (forced extensions by virtue of post processing)
        videofilename = subdct['id'] + '.' + subdct['ext']
        thumbfilename = subdct['id'] + '.jpg'  # jpg enforced by postprocessor
        jsonfilename = subdct['id'] + '.json'
        loc = os.path.join(opts.pathdicts['locdict']['home'], videofilename)
        thumbloc = os.path.join(opts.pathdicts['locdict']['home'], thumbfilename)
        jsonloc = os.path.join(opts.pathdicts['locdict']['home'], jsonfilename)

        # save to JSon file
        with open(jsonloc, 'w') as outfile:
            json.dump(subdct, outfile, indent='\t')

        # Create video object
        videoobject = videomodel.video(0, subdct['id'], subdct['title'], subdct['description'],
                                       subdct['uploader_url'], subdct['view_count'], subdct['webpage_url'],
                                       subdct['like_count'],
                                       subdct['availability'], subdct['duration_string'], subdct['ext'],
                                       subdct['width'],
                                       subdct['height'], subdct['upload_date'], subdct['channel'], subdct['epoch'],
                                       thumbloc, jsonloc, loc)

        # Add or update video to database
        registervideo(videoobject, collection_destination)
    except KeyError as keyerror:
        print(bcolors.WARNING + "Problem parsing video information." + bcolors.ENDC)
        print("{}".format(keyerror))
    except BaseException as exception:
        print(bcolors.WARNING + "Problem parsing video information." + bcolors.ENDC)
        print("{}".format(exception))
