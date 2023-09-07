# Provides options for backup, lazy restore, strict restore.
#   Lazy restore is a restore done on video files.
#   Strict restore is a restore done on backup files.
import json
import os.path
import re

from ..model.db import videomodel
from . import videodownload


# TODO: Add logging & output to show found files


# Class to handle status
class Report:

    def __init__(self, issuccess: bool, message: str):
        self.issuccess = issuccess
        self.message = message


class LocalVideoFiles:
    def __init__(self, videofilename: str, jsonfilename: str, thumbfilename: str, shorturl: str):
        self.videofilename = videofilename
        self.jsonfilename = jsonfilename
        self.thumbfilename = thumbfilename
        self.shorturl = shorturl

    def __str__(self):
        message = ''
        if self.shorturl is not None:
            message += self.shorturl + ': '
        if self.videofilename is not None:
            message += self.videofilename + ', '
        if self.thumbfilename is not None:
            message += self.thumbfilename + ', '
        if self.jsonfilename is not None:
            message += self.jsonfilename
        if message != '':
            return message
        return 'Empty'


class File:  # Another reason windows sucks.
    def __init__(self, basename: str, extension: str):
        self.basename = basename
        self.extension = extension


# Helper function. Using regex it removes the extension from the filename. Returns a File object.
def extractfilename(filename: str) -> File:
    fileregex = r'(.+?)(\.[^.]*$|$)'  # courtesy of stackoverflow
    match = re.search(fileregex, filename)
    file = File(match.group(1), match.group(2))
    return file


# Attempts to recognise video files, add them to database, and save logs for those that it couldn't save properly.
# Accepts target folder as argument, returns ArrayList of video objects found.
def lazyfolderdiscovery(targetfolder: str):
    supportedformats = ['.ogg', '.mp4', '.webm']
    if os.path.isdir(targetfolder):  # check validity of path
        filenamelist = os.listdir(targetfolder)
        fileobjectlist = []
        for entry in filenamelist:  # converts str list to File object list
            fileobjectlist.append(extractfilename(entry))

        localvideoobjects = []

        videofilteredlist = [x for x in fileobjectlist if x.extension in supportedformats]
        jsonfilteredlist = [x for x in fileobjectlist if x.extension == '.json']
        thumbfilteredlist = [x for x in fileobjectlist if x.extension == '.jpg']

        for file in videofilteredlist:
            # create object
            tempvideo = LocalVideoFiles('', '', '', file.basename)
            tempvideo.videofilename = os.path.join(targetfolder, file.basename + file.extension)

            # attempt to find appropriate json
            jsonfile = next((subentry for subentry in jsonfilteredlist if subentry.basename == file.basename and
                             subentry.extension == '.json'), None)
            if jsonfile is not None:
                tempvideo.jsonfilename = os.path.join(targetfolder, jsonfile.basename + jsonfile.extension)

            # attempt to find appropriate image
            jpgfile = next((subentry for subentry in thumbfilteredlist if subentry.basename == file.basename and
                            subentry.extension == '.jpg'), None)
            if jpgfile is not None:
                tempvideo.thumbfilename = os.path.join(targetfolder, jpgfile.basename + jpgfile.extension)

            # append to video object list
            localvideoobjects.append(tempvideo)

        return localvideoobjects
    else:
        print("Path is not a valid folder.")


# Creates the video objects and inserts them in the database.
def lazyrestore(targetfolder: str):
    localvideos = lazyfolderdiscovery(targetfolder)
    if localvideos is not None:
        for localvideo in localvideos:
            # extract video info from json
            if localvideo.jsonfilename is not None:
                dbvideo = parsejsoninfo(localvideo.jsonfilename)

                # add remaining info
                if localvideo.jsonfilename is not None:
                    dbvideo.jsonloc = localvideo.jsonfilename
                if localvideo.thumbfilename is not None:
                    dbvideo.thumbnail = localvideo.thumbfilename
                if localvideo.videofilename is not None:
                    dbvideo.loc = localvideo.videofilename

                # edge case:
                if (localvideo.jsonfilename is None or localvideo.jsonfilename == ''
                        and localvideo.videofilename is not None):
                    dbvideo.title = localvideo.videofilename
                    dbvideo.availability = 'Local'

                # Register video
                videodownload.registervideo(dbvideo)
            else:  # Couldn't extract json data
                pass  # TODO: Do this properly

    else:
        pass  # TODO: Do this properly


# Takes in json file, gets the important contents for the video in the database, and returns a video object.
# TODO: Replace with the newer implementation in json video object
def parsejsoninfo(jsonloc: str) -> videomodel.video:
    keys = ['id']  # important keys that MUST be present in the json
    if jsonloc is not None and jsonloc != '':  # if json file is found, extract info
        with open(jsonloc) as jsonfile:
            data = json.load(jsonfile)

            # TODO: is this the right approach?
            for key in keys:
                if key not in data:
                    return None

            # using .get() to have a default value set
            id = 0  # default value, id is for db purposes, shorturl is the dict's id
            shorturl = data.get('id')
            title = data.get('title')
            description = data.get('description')
            uploader_url = data.get('uploader_url')
            view_count = data.get('view_count')
            webpage_url = data.get('webpage_url')
            like_count = data.get('like_count')
            availability = data.get('availability')
            duration_string = data.get('duration_string')
            ext = data.get('ext')
            width = data.get('width')
            height = data.get('height')
            upload_date = data.get('upload_date')
            channel = data.get('channel')
            epoch = data.get('epoch')

            # this is useless because it will be overwritten by the found data afterwards anyway
            # TODO: Is it better to keep the json info or the 'discovered' info? Which of the two approaches is less prone
            #       to errors?
            '''thumbnail = data['thumbnail']
            jsonloc = data['jsonloc']
            loc = data['loc']'''

        # set up video object
        video = videomodel.video(id, shorturl, title, description, uploader_url, view_count, webpage_url, like_count,
                                 availability, duration_string, ext, width, height, upload_date, channel, epoch,
                                 '', '', '')
    else:  # if json file is not found, attempt to create video anyway
        video = videomodel.video(0, '', '', '', '', '', '',
                                 '', '', '', '', '', '', '',
                                 '', '', '', '', '')

    return video
