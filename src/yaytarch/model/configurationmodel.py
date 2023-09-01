from db import get_db
from tools.outputformat import bcolors


class configuration:

    def __init__(self, downloadlocation, ytdlpargs, jsonargs):
        self.downloadlocation = downloadlocation
        self.ytdlpargs = ytdlpargs
        self.jsonargs = jsonargs


# Fetches configuration object
def fetchconfiguration():
    db = get_db()

    try:
        result = db.execute('SELECT * FROM configuration').fetchone()  # There should only be one anyway
    except db.Error as db_error:
        print(bcolors.WARNING + "Database error:" + bcolors.ENDC)
        print("{}".format(db_error))
        return None
    if result is not None:
        configurationobject = configuration(result['downloadlocation'], result['ytdlpargs'], result['jsonargs'])
        return configurationobject
    return None


# Function used to initialise db. This should only be run once.
def initialconfiguration(configuration):
    db = get_db()

    try:
        result = db.execute(
            "INSERT INTO configuration(downloadlocation, ytdlpargs, jsonargs) VALUES (?, ?, ?)",
            (configuration.downloadlocation, configuration.ytdlpargs, configuration.jsonargs), )

        db.commit()
    except db.Error as db_error:
        print("{}".format(db_error))
        return None
    except db.IntegrityError as db_error:
        print("{}".format(db_error))
    if result is not None:
        print(bcolors.OKCYAN + "Initial configuration saved." + bcolors.ENDC)
        return
    raise Exception("Unable to initialise db.")


# TODO
def updateconfiguration(configuration):
    pass
