# This module provides a class object for videos and helper methods to fetch and insert videos. Any data coherence
# check should be done here.
# The difference between the other videomodel is that this will fetch information from json file and probably be more
# flexible. The vision is to also make it more extensible should requested tags to download change.
import json

# Filter for unwanted keys. TODO: Ideally, this should be fetched by configuration.
def keyfilter(pair):
    filters = ['title']

    key, value = pair
    for unwanted in filters:
        if key == unwanted:
            return False
        else:
            return True


class video:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    # TODO: Dummy function. It will be responsible to make sure the bare minimum tags are present.
    def coherencycheck(self):
        pass


# This function is responsible for parsing a specified json file and returning the appropriate video object.
# Returns None if generation failed.
def generatevideofromjsonfile(filename: str) -> video:
    keys = ['id', 'title']  # important keys that MUST be present in the json

    if filename is not None and filename != '':  # if json file is found, extract info
        with open(filename) as jsonfile:
            data = json.load(jsonfile)

            # Remove unwanted keys. Necessary because jsons can get big.
            # A performance study should be done to see if it's worth it.
            # TODO: This is a horrible approach and may destroy performance
            data = dict(filter(keyfilter, data.items()))

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
