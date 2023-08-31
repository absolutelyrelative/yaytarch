# When backend is set to work with json files, this will be used to fetch configuration on a folder by folder basis.
# TODO: Finish. There are three types of backend: 1) Full database, 2) Mixed DB - json, 3) Local self contained
#       This solution is for 3) which will come after 2) is completed.
import json

class configuration:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# This function is responsible for parsing a specified json file and returning the appropriate video object.
# Returns None if generation failed.
def generateconfigfromjsonfile(filename: str) -> configuration:

    if filename is not None and filename != '':  # if json file is found, extract info
        with open(filename) as jsonfile:
            data = json.load(jsonfile)

            extractedconfig = configuration()
            for key, value in data.items():
                extractedconfig.__setattr__(key, value)

            return extractedconfig
