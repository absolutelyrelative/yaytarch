import json
import os

from yt_dlp import YoutubeDL

from ..model.db import collectionmodel, videomodel
from .outputformat import bcolors
from .config import DlOptions, DlArguments
from .urltools import *


# Helper function to begin the download process by only specifying id. Useful for refreshing videos on the webpage.
def dlbyid(videoid: int):
    videoobjecttoupdate = videomodel.getvideobyid(videoid)
    if videoobjecttoupdate is None:
        raise Exception(
            bcolors.FAIL + "Couldn't find collection by videoid. Please report this bug, it should never happen." + bcolors.ENDC)
    else:
        print(bcolors.OKCYAN + "Updating video " + bcolors.BOLD)
        print(videoobjecttoupdate.title)
        print(bcolors.ENDC)
        dl(videoobjecttoupdate.shorturl)


# Helper function to begin the download process by only specifying id. Useful for refreshing collections on the webpage.
def dlplaylistbyid(collectionid: int):
    collectionobjecttoupdate = collectionmodel.getvideocollectionbyid(collectionid)
    if collectionobjecttoupdate is None:
        raise Exception(
            bcolors.FAIL + "Couldn't find collection by collectionid. Please report this bug, it should never happen." + bcolors.ENDC)
    else:
        print(bcolors.OKCYAN + "Updating collection " + bcolors.BOLD + collectionobjecttoupdate.title + bcolors.ENDC)

        # Checking if collection is local
        if collectionobjecttoupdate.shorturl != "":
            dl(collectionobjecttoupdate.shorturl)
        else:
            print(
                bcolors.FAIL + "Couldn't update collection, it is a local collection with an unspecified url." + bcolors.ENDC)


# Helper function to refresh all videos with a valid short url
def refreshallvideos():
    print(bcolors.OKCYAN + "Refreshing all videos with a valid short url..." + bcolors.ENDC)
    videos = videomodel.getallvideos()
    for video in videos:
        dl(video.shorturl)


# Gets video or playlist by link, automatically generates collection for playlists, and adds videos to
# respective collections.
# If local is True, downloads the video, saves json and thumb, but does not add it to database.
def dl(link, collection_destination=None, local=False):
    opts = DlOptions(None, local)

    with YoutubeDL(opts.ytdlp_options) as ydl:
        print(bcolors.OKCYAN + "Downloading & parsing information..." + bcolors.ENDC)
        # with contextlib.suppress(Exception):  # Necessary to suppress ytdlp exceptions in a playlist
        # try:
        info = ydl.extract_info(link, download=False)
        # except yt_dlp.utils.DownloadError as dlerror:
        #    pass
        dictdump = ydl.sanitize_info(info)

        # Get video type
        # TODO: private, unlisted videos show as Nonetype in dictdump, it's impossible to extract id and save changes.
        #       One way to solve this is to refresh using local shorturls.
        if dictdump is not None:
            print(bcolors.OKCYAN + "Downloading videos..." + bcolors.ENDC)
            match dictdump['_type']:
                case 'video':  # single video
                    # Download the video
                    ydl.download(link)
                    # Process the video, locally if necessary
                    parsevideoinfo(dictdump, collection_destination, local)

                # PROBLEM! ONLY this is called when playlists are found, it doesn't cycle through.
                case 'playlist':  # playlist AND channels
                    # Download the playlist
                    ydl.download(link)

                    # Process the playlist, locally if necessary
                    parseplaylistinfo(dictdump, local)

                case _:  # may be required for other platforms / channels
                    pass
        else:
            # TODO: Add to database anyway and mark it as not downloaded.
            print(bcolors.BOLD + bcolors.FAIL + "Could not download video, skipping..." + bcolors.ENDC)
            if local == False:  # TODO: Find a way to do this when local is True
                updatehiddenstatus(link)


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
            bcolors.OKCYAN + "Video entry already exists. Updating " + bcolors.BOLD, end='')
        print(videoobjecttoupdate.title, end='')
        print(bcolors.ENDC, end=': ')
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


# Helper function to configure videos for local use. If local is True, it operates without a db.

def parsevideoinfo(dictdump, collection_destination=None, local=False):
    opts = DlOptions(None, local)

    try:
        # Parse keys we need
        # TODO: Change this for local usage ?
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

        if local is False:  # add to database only if local is False
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


# Helper function to configure playlists for local use.

def parseplaylistinfo(dictdump, local=False):
    opts = DlOptions(None, local)

    try:
        # Cycle through keys
        playlistsubdct = {key: dictdump[key] for key in DlArguments.playlistkeys}
        thumbnailssubdct = dictdump['thumbnails']
        # extract downloaded thumbnail location
        thumbnailloc = ""  # Just in case no thumbnail has been downloaded
        for thumbnail in thumbnailssubdct:
            if "filepath" in thumbnail:
                thumbnailloc = thumbnail["filepath"]

        # save to JSon file
        jsonfilename = playlistsubdct['id'] + '.json'
        jsonloc = os.path.join(opts.pathdicts['locdict']['home'], jsonfilename)
        with open(jsonloc, 'w') as outfile:
            json.dump(playlistsubdct, outfile, indent='\t')

        registerplaylist(playlistsubdct, thumbnailloc, jsonloc, local)
    except KeyError as keyerror:
        print(bcolors.WARNING + "Problem adding video." + bcolors.ENDC)
        print("{}".format(keyerror))


# Creates collection entry and registers to specified collection. Cycles and parses through each video of the playlist
#   and registers it to the collection. If local is True, it operates without a db.

def registerplaylist(playlistsubdct, thumbnailloc, jsonloc, local=False):
    opts = DlOptions(None)

    if local == False:  # create new collection object
        newcollection = collectionmodel.videocollection(0, playlistsubdct['id'],
                                                        playlistsubdct['title'],
                                                        playlistsubdct['availability'],
                                                        playlistsubdct['modified_date'],
                                                        playlistsubdct['playlist_count'],
                                                        playlistsubdct['uploader_url'],
                                                        playlistsubdct['epoch'], thumbnailloc,
                                                        jsonloc)

        # Check if collection already exists
        oldcollection = collectionmodel.findcollectionbyshorturl(playlistsubdct['id'])
        if oldcollection is None:
            print(bcolors.OKCYAN + "Collection doesn't exist. Creating..." + bcolors.ENDC)
            newcollectionid = collectionmodel.createvideocollectionentry(newcollection)
            if newcollectionid is None:
                raise Exception("Could not create video collection entry.")
        else:
            print(bcolors.OKCYAN + "Collection already exists. Updating videos..." + bcolors.ENDC)
            collectionmodel.updatecollectionentry(oldcollection,
                                                  newcollection)

    # try to register each video individually
    # because of course the video entries in the playlist info don't share the same keys.
    with YoutubeDL(opts.ytdlp_options) as ydl:
        for entry in playlistsubdct['entries']:
            # TODO: Find a better, more universal solution. This check on availability might only work on yt.
            # Redownload information
            if entry is not None and (entry['availability'] != 'public' or entry[
                'availability'] != 'unlisted'):  # entry is none if video is blocked / private (?)
                info = ydl.extract_info(entry['id'], download=False)
                dictdump = ydl.sanitize_info(info)

                # Process the video locally
                parsevideoinfo(dictdump, playlistsubdct['title'], local)


# Attempt to extract short url from unavailable video link for updating purposes.
# it's necessary for deleted/private/unlisted videos to properly search matches in the database by
# extracting short url, something yt-dlp does not take care of in these cases.
# TODO: Fix for local use
def updatehiddenstatus(link):
    shurl = converttoshurl(link) if isurl(link) else link

    videotohide = videomodel.getvideobyshorturl(shurl)
    if videotohide is not None:
        videotohide.availability = "private/unlisted"
        registervideo(videotohide)
    else:
        print(bcolors.FAIL + "Could not find video locally to update status." + bcolors.ENDC)
