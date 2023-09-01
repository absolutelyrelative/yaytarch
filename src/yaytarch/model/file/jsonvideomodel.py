# This module provides a class object for videos and helper methods to fetch and insert videos. Any data coherence
# check should be done here.
# The difference between the other videomodel is that this will fetch information from json file and probably be more
# flexible. The vision is to also make it more extensible should requested tags to download change.

# yt-dlp will save most things in the JSON apart from some very problematic keys, and therefore the structure of
# the json itself should not change much. These filters only apply to what the user wants to show.
import json
# from ...tools import backup
from src.yaytarch.tools.backup import *


# Filter for unwanted keys. TODO: Ideally, this should be fetched by configuration.
def unwantedkeyfilter(pair):
    filters = []

    key, value = pair
    for unwanted in filters:
        if key == unwanted:
            return True
        else:
            return False


class video:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# Singleton for a globally accessible, more resource efficient, list of discovered things.
class folderdiscoveryresult(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(folderdiscoveryresult, cls).__new__(cls)
        return cls.instance

    #  Return entry corresponding to shurl (name file without extensions)
    #  TODO: Really, please, find a better name for this. Tech debt is increasing exponentially.
    def find_discovered_entry(self, shurl: str):
        if hasattr(self, 'discovered'):
            for entry in self.discovered:
                if entry.shorturl == shurl:
                    return entry


# This function is responsible for parsing a specified json file and returning the appropriate video object.
# Returns None if generation failed.
def generatevideofromjsonfile(filename: str) -> video:
    keys = ['id', 'title']  # important keys that MUST be present in the json

    if filename is not None and filename != '':  # if json file is found, extract info
        with open(filename) as jsonfile:
            data = json.load(jsonfile)

            # Remove unwanted keys. Necessary because jsons can get big.
            # A performance study should be done to see if it's worth it.
            # TODO: This is a horrible approach and may destroy performance.
            #        It is also not working correctly. Fix.
            #  data = dict(filter(unwantedkeyfilter, data.items()))

            # TODO: is this the right approach?
            for key in keys:
                if key not in data:
                    return None

            extractedvideo = video()
            for key, value in data.items():
                # PAY ATTENTION: HERE THERE IS NO SHORTURL, BUT ONLY ID IN JSON! NO DATABASE -> NO ID
                if key != 'id':
                    extractedvideo.__setattr__(key, value)
                else:
                    extractedvideo.__setattr__('shorturl', value)

            return extractedvideo


# Appends the generated video from json objects to the lazy discovery array, and attaches the list to the singleton.
def folderdiscovery(location):
    results = lazyfolderdiscovery(location)
    videoobjectlist = []

    for entry in results:
        if entry.jsonfilename is not None and entry.jsonfilename != '':
            video = generatevideofromjsonfile(entry.jsonfilename)
            videoobjectlist.append(video)
            # results.__getitem__(entry)
            entry.__setattr__('localvideoobj', video)

    singleton = folderdiscoveryresult()
    singleton.__setattr__('discovered', results)
    singleton.__setattr__('videoobjects',
                          videoobjectlist)  # TODO: I think this is redundant. Discovered already has this inside entry.
