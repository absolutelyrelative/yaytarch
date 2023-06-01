# Provides a quieter download experience
# self.params['logger'].warning(message)
# self.params['logger'].error(message)
# self.params['logger'].debug(message)
from tools.outputformat import bcolors


class dllogger:
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
        print(bcolors.OKCYAN + "Finished" + bcolors.ENDC)