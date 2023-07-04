DROP TABLE IF EXISTS video;
DROP TABLE IF EXISTS videocollection;
DROP TABLE IF EXISTS videocollectionmembership;
DROP TABLE IF EXISTS configuration;

CREATE TABLE video (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Can't use shorturl as id because of future local videos integration
    shorturl TEXT DEFAULT "",
    title TEXT DEFAULT "",
    description TEXT DEFAULT "",
    uploader_url TEXT DEFAULT "",
    view_count INT DEFAULT 0,
    webpage_url TEXT DEFAULT "",
    like_count INT DEFAULT 0,
    availability TEXT DEFAULT "",
    duration_string TEXT DEFAULT "",
    ext TEXT DEFAULT "",
    width INT DEFAULT 320,
    height INT DEFAULT 240,
    upload_date TEXT DEFAULT "",
    channel TEXT DEFAULT "",
    epoch INT DEFAULT 0,

    thumbnail TEXT DEFAULT "", -- custom, not from json (thumbnail location)
    jsonloc TEXT DEFAULT "", -- custom, specifies where the json file is for future use
    loc TEXT UNIQUE NOT NULL --custom
);

CREATE TABLE videocollection (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Can't use playlist shorturl id because local playlists don't have one
    shorturl TEXT DEFAULT "",
    title TEXT DEFAULT "",
    availability TEXT DEFAULT "",
    modified_date TEXT DEFAULT "",
    playlist_count INT DEFAULT 0,
    uploader_url TEXT DEFAULT "",
    epoch INT DEFAULT 0,

    thumbnail TEXT DEFAULT "", -- custom, not from json (thumbnail location)
    jsonloc TEXT DEFAULT "" -- custom, specifies where the json file is for future use
);

CREATE TABLE videocollectionmembership (
    videoid INTEGER NOT NULL,
    collectionid INTEGER NOT     NULL,
    FOREIGN KEY (videoid) REFERENCES video (id),
    FOREIGN KEY (collectionid) REFERENCES videocollection (id)
);

CREATE TABLE configuration (
    downloadlocation TEXT DEFAULT "",
    ytdlpargs TEXT DEFAULT "",
    jsonargs TEXT DEFAULT ""
);

INSERT INTO videocollection(title)
VALUES ("All videos");
INSERT INTO configuration(downloadlocation, ytdlpargs, jsonargs)
VALUES ("","","");