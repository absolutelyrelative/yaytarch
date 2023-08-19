# yaytarch
Yet Another YouTube Archival (tool)

Yaytarch is a local library tool that allows you to watch content which you downloaded, locally from your browser.
It tries to fill a big gap of low resource intensive media libraries, and the use case is to bring my disorder of downloaded videos and playlists to an neat end. 

It is a yt-dlp frontend built with python & flask and it allows you to:

- Download and update videos from the browser or CLI
- Download and update playlists from the browser or CLI
- Browse and watch videos
- Create local collections of videos
- (Soon) import local videos!

## Collections view
  ![yaytarch_collectionview](https://github.com/absolutelyrelative/yaytarch/blob/main/images/collection_view.png?raw=true)

## Video list view
![yaytarch_videolistview](https://github.com/absolutelyrelative/yaytarch/blob/main/images/videolist_view.png?raw=true)

## Video view
![yaytarch_videoview](https://github.com/absolutelyrelative/yaytarch/blob/main/images/video_view.png?raw=true)

## Installation:
You can choose to install the official release from PyPi or you can also build your own version:

### Installation through pypi:
Fetch and install yaytarch and its dependencies:

`pip install yaytarch`

And you're good to go, you can skip manual installation!

### Build and install manually and locally:
Clone the repository:

`git clone https://github.com/absolutelyrelative/yaytarch.git`

Build wheel:

`python -m build --wheel`

a dist/yaytarch-xx.whl will be generated.

Install wheel:

`pip install yaytarch-xx.whl`




## Usage:

### Initialise configuration:
In order to run the app, a default download location needs to be given:

`flask --app yaytarch init-db C:\PATH\TO\STORAGE\`

### View videos:
In order to browse videos locally you can use:

`flask --app yaytarch run`

NOTE: THIS is NOT the correct approach for deployment to a server. You NEED to set-up a correct secret key!
Further information will come, for now see https://flask.palletsprojects.com/en/2.3.x/tutorial/deploy/#build-and-install

I take no responsibility in bad usage!

### Download video, playlist, or channel:
Playlists will be organised automatically, single videos will be saved to the generic 'All Videos' category

`flask --app yaytarch dl LINK`


### Lazy restore:
In case of any issue, you can always re-initialise the database and restore your previous progress. There will be two restore options, this is the so called 'lazy restore' which works by folder discovery. It should be used mainly when the database is unavailable.
It can also be used to add local videos to the database, but a better way to do so will come soon.

`flask --app yaytarch lazyrestore C:\PATH\TO\VIDEOS`

Future features:
- A less bad CSS / Style.
- Others (will specify soon when I import my todo list)

