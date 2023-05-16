DROP TABLE IF EXISTS video;
DROP TABLE IF EXISTS videocollection;
DROP TABLE IF EXISTS videocollectionmembership;

CREATE TABLE video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shorturl TEXT UNIQUE NOT NULL,
    loc TEXT UNIQUE NOT NULL,
    downloaded BOOLEAN DEFAULT 0
);

CREATE TABLE videocollection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vcname TEXT NOT NULL,
    shorturl TEXT UNIQUE --Collections are treated locally to nullify same video redownload, therefore shorturl can be null
);

CREATE TABLE videocollectionmembership (
    videoid INTEGER NOT NULL,
    collectionid INTEGER NOT NULL,
    FOREIGN KEY (videoid) REFERENCES video (id),
    FOREIGN KEY (collectionid) REFERENCES videocollection (id)
);