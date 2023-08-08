# Provides options for backup, lazy restore, strict restore.
#   Lazy restore is a restore done on video files.
#   Strict restore is a restore done on backup files.

import os.path
import re


# Custom exceptions for importing operation
class ImportException(Exception):
    def __init__(self, message):
        self.message = message


# Class to handle status
class Report:

    def __init__(self, issuccess: bool, message: str):
        self.issuccess = issuccess
        self.message = message


class LocalVideoFiles:
    def __init__(self, videofilename: str, jsonfilename: str, thumbfilename: str):
        self.videofilename = videofilename
        self.jsonfilename = jsonfilename
        self.thumbfilename = thumbfilename

    # Generates a videomodel instance
    def returnvideoobject(self):
        pass


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
        for file in fileobjectlist:
            if file.extension in supportedformats:
                # create object
                tempvideo = LocalVideoFiles('', '', '')
                tempvideo.videofilename = file.extension

                # attempt to find appropriate json
                jsonfile = next((subentry for subentry in fileobjectlist if subentry.basename == file.basename and
                                 subentry.extension == '.json'), None)
                if jsonfile is not None:
                    tempvideo.jsonfilename = os.path.join(targetfolder, jsonfile.basename + jsonfile.extension)
                    fileobjectlist.remove(jsonfile)

                # attempt to find appropriate image
                jpgfile = next((subentry for subentry in fileobjectlist if subentry.basename == file.basename and
                                subentry.extension == '.jpg'), None)
                if jpgfile is not None:
                    tempvideo.thumbfilename = os.path.join(targetfolder, jpgfile.basename + jpgfile.extension)
                    fileobjectlist.remove(jpgfile)

                # remove entry from fileobjects
                fileobjectlist.remove(file)
                # append to video object list
                localvideoobjects.append(tempvideo)

        return localvideoobjects
    else:
        pass  # TODO: Add exception ?

# Creates the video objects and inserts them in the database.
def lazyrestore(targetfolder: str):
    localvideos = lazyfolderdiscovery(targetfolder)
    if localvideos is not None:
        pass
    else:
        pass  # TODO: Do this properly


# Takes in json file, gets the important contents for the video in the database, and returns a video object.
def parsejsoninfo():
    pass
