DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS video;
DROP TABLE IF EXISTS clip;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE video (
  filename TEXT PRIMARY KEY,
  filename_no_ext TEXT NOT NULL,
  streamer TEXT NOT NULL,
  date TEXT NOT NULL,
  title TEXT NOT NULL
);

CREATE TABLE clip (
  filename TEXT PRIMARY KEY,
  video_filename_no_ext TEXT NOT NULL,
  state int NOT NULL
);

CREATE TABLE path (
    p TEXT
)
