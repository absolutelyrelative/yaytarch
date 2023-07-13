import click
from flask import (
    Blueprint, render_template, send_from_directory, request
)

from .tools import videodownload
from .tools.config import *
from .model import videocollectionrelmodel
from .model import videomodel

# This blueprint takes care of the video view page and any future feature of it

bp = Blueprint('videos', __name__)


# TODO: Remove ability to remove videos from "All Collections"?
@bp.route('/video/<int:videoid>', methods=['GET', 'POST'])
def viewvideo(videoid):
    if request.method == 'POST':
        # Request type: Remove
        if 'valueR' in request.form.keys():  # Remove from playlist buttom
            message = videocollectionrelmodel.removevideocollectionmembershipentry(videoid, request.form['valueR'])

        # Request type: Add
        if 'value' in request.form.keys():  # Add to playlist button
            if videomodel.addvideotocollection(videoid, request.form['value']) is not None:
                message = "Video added to collection"
            else:
                message = "Video already part of collection."

        # Request type: Refresh
        if 'buttonrefresh' in request.form.keys():
            videodownload.dlbyid(videoid)

    # Fetch all collections the video is in to display values
    incollections = videocollectionrelmodel.getvideocollectionmembershipbyid(videoid)
    # Fetch all collections the video is NOT in to display values
    notincollections = videocollectionrelmodel.getinversedvideocollectionmembershipbyid(videoid)
    video = videomodel.getvideobyid(videoid)
    return render_template('videoplay.html', video=video, incollections=incollections,
                           notincollections=notincollections)


@bp.route("/video/source/<int:videoid>")
def load_video(videoid):
    video = videomodel.getvideobyid(videoid)

    file_name = os.path.basename(video.loc)
    dir_name = os.path.dirname(video.loc)

    return send_from_directory(dir_name, file_name)


# TODO: If this works, merge with load_video to save half the IO calls.
@bp.route("/video/source/thumb/<int:videoid>")
def load_picture(videoid):
    video = videomodel.getvideobyid(videoid)
    dirname = os.path.dirname(video.thumbnail)
    filename = os.path.basename(video.thumbnail)

    return send_from_directory(dirname, filename)


@bp.cli.command("dl")
@click.argument("link")
def dl(link):
    videodownload.dl(link)
