-- Create tables in replica database
CREATE SEQUENCE IF NOT EXISTS fact_history_id_seq;

-- Create dim_artist table
CREATE TABLE IF NOT EXISTS dim_artist (
    artist_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    external_url TEXT NOT NULL,
    follower_count INTEGER NOT NULL,
    image_url TEXT,
    popularity INTEGER NOT NULL
);

-- Create dim_album table
CREATE TABLE IF NOT EXISTS dim_album (
    album_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    total_tracks INTEGER NOT NULL,
    release_date TIMESTAMP(3) WITHOUT TIME ZONE NOT NULL,
    external_url TEXT NOT NULL,
    image_url TEXT,
    label TEXT NOT NULL,
    popularity INTEGER NOT NULL
);

-- Create dim_song table
CREATE TABLE IF NOT EXISTS dim_song (
    song_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    disc_number INTEGER NOT NULL,
    duration_ms BIGINT NOT NULL,
    explicit BOOLEAN NOT NULL,
    external_url TEXT NOT NULL,
    preview_url TEXT,
    popularity INTEGER NOT NULL
);

-- Create fact_history table with foreign key constraints
CREATE TABLE IF NOT EXISTS fact_history (
    id INTEGER PRIMARY KEY DEFAULT nextval('fact_history_id_seq'),
    song_id TEXT NOT NULL,
    artist_id TEXT NOT NULL,
    album_id TEXT NOT NULL,
    played_at TIMESTAMP(3) WITHOUT TIME ZONE NOT NULL,
    FOREIGN KEY (song_id) REFERENCES dim_song(song_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (artist_id) REFERENCES dim_artist(artist_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (album_id) REFERENCES dim_album(album_id) ON UPDATE CASCADE ON DELETE RESTRICT
);