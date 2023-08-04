# Provides a quieter download experience
# self.params['logger'].warning(message)
# self.params['logger'].error(message)
# self.params['logger'].debug(message)
import os.path

from ..model import configurationmodel
from .outputformat import bcolors


class DlLogger:
    def debug(self, *args):
        pass

    def info(self, *args):
        pass

    def warning(self, *args):
        pass

    def error(self, *args):
        pass

    def downloading(self, *args):
        pass

    # {'filename': '....mp4', 'status': 'finished', 'total_bytes': 4879715, 'info_dict': {...} }
    # From ytdlp source, error, downloading are always called at least once. finished() should be called only
    # if download has been completed succesfully.

    # progress_hooks:    A list of functions that get called on download
    #                        progress, with a dictionary with the entries
    #                        * status: One of "downloading", "error", or "finished".
    #                                  Check this first and ignore unknown values.
    #                        * info_dict: The extracted info_dict
    #
    #                        If status is one of "downloading", or "finished", the
    #                        following properties may also be present:
    #                        * filename: The final filename (always present)
    #                        * tmpfilename: The filename we're currently writing to
    #                        * downloaded_bytes: Bytes on disk
    #                        * total_bytes: Size of the whole file, None if unknown
    #                        * total_bytes_estimate: Guess of the eventual file size,
    #                                                None if unavailable.
    #                        * elapsed: The number of seconds since download started.
    #                        * eta: The estimated time in seconds, None if unknown
    #                        * speed: The download speed in bytes/second, None if
    #                                 unknown
    #                        * fragment_index: The counter of the currently
    #                                          downloaded video fragment.
    #                        * fragment_count: The number of fragments (= individual
    #                                          files that will be merged)
    #
    #                        Progress hooks are guaranteed to be called at least once
    #                        (with status "finished") if the download is successful.
    def finished(self, *args):
        status = ''
        title = ''
        completion = ''
        filename = ''

        for arg in args:  # Are there cases in which some of these are present but not all ?
            if 'status' in arg:
                status = arg['status']
            if 'info_dict' in arg:
                title = arg['info_dict']['title']
            if '_default_template' in arg:
                completion = arg['_default_template']
            if 'filename' in arg:
                filename = arg['filename']

            # This is horrible, but windows console is not great to print.
            if status != "downloading":  # TODO: Find a more elegant solution, windows console broke this
                print(bcolors.BOLD + bcolors.OKCYAN, end='')
                print(status.encode("cp1252", errors="ignore"), end='')
                print(bcolors.ENDC, end='')

                print(bcolors.OKCYAN + ' downloading video: ' + bcolors.BOLD, end='')
                print(title.encode("cp1252", errors="ignore"))


# Function to generate and return ytdlp options
class DlOptions:
    # Set up object
    def __init__(self, folderloc):
        # Fetch path from db
        configuration = configurationmodel.fetchconfiguration()
        downloadpath = configuration.downloadlocation

        # Make sure path is set up correctly
        if os.path.isdir(downloadpath):
            downloadpath = os.path.join(downloadpath, "")

        if folderloc is None:
            folderloc = "yaylib"

        # Paths dictionary
        self.pathdicts = {
            'locdict': {
                'home': os.path.join(downloadpath, folderloc)
            },
            'outputtemplatedict': {
                'default': "%(id)s.%(ext)s"
            }
        }

        # List to tidy up logs
        self.loggerlist = [DlLogger().downloading, DlLogger().finished, DlLogger().error]

        self.ytdlp_options = {'paths': self.pathdicts['locdict'], 'outtmpl': self.pathdicts['outputtemplatedict'],
                              'format': 'mp4',
                              'writethumbnail': True, 'logger': DlLogger(), 'progress_hooks': self.loggerlist,
                              # Post-processing to force thumbnail conversion to jpg. Hacky but only playlists
                              # give file output name for thumbnails.
                              'postprocessors': [{
                                  'key': 'FFmpegThumbnailsConvertor',
                                  'format': 'jpg',
                              }]
                              }


class DlArguments:
    videokeys = ['id', 'title', 'thumbnail', 'description', 'uploader_url', 'view_count', 'webpage_url', 'like_count',
                 'availability', 'duration_string', 'ext', 'width', 'height', '_type', 'upload_date', 'channel',
                 'epoch']

    playlistkeys = ['id', 'title', 'availability', 'modified_date', 'playlist_count', 'uploader_url',
                    '_type', 'epoch', 'entries']
