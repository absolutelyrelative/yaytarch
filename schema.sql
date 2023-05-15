DROP TABLE IF EXISTS video;
DROP TABLE IF EXISTS collection;
DROP TABLE IF EXISTS videocollectionmembership;

CREATE TABLE video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shorturl TEXT UNIQUE NOT NULL,
    loc TEXT UNIQUE NOT NULL,
    downloaded BOOLEAN DEFAULT 0
);

CREATE TABLE collection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shorturl TEXT UNIQUE, --Collections are treated locally to nullify same video redownload, therefore shorturl can be null
);

CREATE TABLE videocollectionmembership (
    videoid INTEGER NOT NULL,
    collectionid INTEGER NOT NULL,
    FOREIGN KEY (videoid) REFERENCES video(id),
    FOREIGN KEY (collectionid) REFERENCES collection(id)
)