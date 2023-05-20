DROP TABLE IF EXISTS video;
DROP TABLE IF EXISTS videocollection;
DROP TABLE IF EXISTS videocollectionmembership;

CREATE TABLE video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shorturl TEXT UNIQUE NOT NULL,
    title TEXT DEFAULT "",
    width INT DEFAULT 320,
    height INT DEFAULT 240,
    loc TEXT UNIQUE NOT NULL,
    descr TEXT DEFAULT "",
    resolution TEXT DEFAULT "",
    downloaded BOOLEAN DEFAULT 0
);

CREATE TABLE videocollection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vcname TEXT NOT NULL,
    shorturl TEXT DEFAULT "" --Collections are treated locally to nullify same video redownload, therefore shorturl can be null
);

CREATE TABLE videocollectionmembership (
    videoid INTEGER NOT NULL,
    collectionid INTEGER NOT NULL,
    FOREIGN KEY (videoid) REFERENCES video (id),
    FOREIGN KEY (collectionid) REFERENCES videocollection (id)
);

INSERT INTO videocollection(vcname, shorturl)
VALUES ("All videos", "");