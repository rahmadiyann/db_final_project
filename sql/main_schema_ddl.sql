-- Create tables in replica database
CREATE SEQUENCE IF NOT EXISTS fact_history_id_seq;
CREATE SCHEMA IF NOT EXISTS analysis;
CREATE SCHEMA IF NOT EXISTS metrics;
-- Create dim_artist table
CREATE TABLE IF NOT EXISTS dim_artist (
    artist_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    external_url TEXT NOT NULL,
    follower_count INTEGER NOT NULL,
    image_url TEXT,
    popularity INTEGER NOT NULL,
    added_at TIMESTAMP(3) WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
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
    popularity INTEGER NOT NULL,
    added_at TIMESTAMP(3) WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
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
    popularity INTEGER NOT NULL,
    added_at TIMESTAMP(3) WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create fact_history table with foreign key constraints
CREATE TABLE IF NOT EXISTS fact_history (
    id INTEGER PRIMARY KEY DEFAULT nextval('fact_history_id_seq'),
    song_id TEXT NOT NULL,
    artist_id TEXT NOT NULL,
    album_id TEXT NOT NULL,
    played_at TIMESTAMP(3) WITHOUT TIME ZONE NOT NULL,
    added_at TIMESTAMP(3) WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES dim_song(song_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (artist_id) REFERENCES dim_artist(artist_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (album_id) REFERENCES dim_album(album_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS analysis.album_completion_analysis (
    album_title VARCHAR(255),
    artist_name VARCHAR(255),
    total_tracks INT,
    unique_tracks_played INT,
    completion_percentage FLOAT,
    listening_status VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS analysis.song_duration_preference (
    duration_category VARCHAR(255),
    play_count INT,
    percentage FLOAT
);

CREATE TABLE IF NOT EXISTS analysis.explicit_preference (
    explicit BOOLEAN,
    play_count INT,
    percentage FLOAT
);

CREATE TABLE IF NOT EXISTS analysis.day_of_week_listening_distribution (
    day_of_week VARCHAR(255),
    play_count INT,
    unique_songs INT,
    unique_artists INT,
    song_variety_percentage FLOAT,
    artist_variety_percentage FLOAT
);

CREATE TABLE IF NOT EXISTS analysis.session_between_songs (
    session_type VARCHAR(255),
    count INT,
    percentage FLOAT
);

CREATE TABLE IF NOT EXISTS analysis.song_popularity_distribution (
    popularity_bracket INT,
    play_count INT,
    popularity_range VARCHAR(10),
    percentage FLOAT
);

CREATE TABLE IF NOT EXISTS analysis.hour_of_day_listening_distribution (
    hour_of_day INT,
    play_count INT,
    percentage FLOAT
);

CREATE TABLE IF NOT EXISTS analysis.album_release_year_play_count (
    release_year INT,
    play_count INT
);

CREATE TABLE IF NOT EXISTS metrics.statistics (
    total_ms_listened INT,
    total_song_played INT
);

CREATE TABLE IF NOT EXISTS metrics.artist_longest_streak (
    artist_id VARCHAR(255),
    artist_name VARCHAR(255),
    streak INT,
    date_from DATE,
    date_until DATE,
    total_minutes INT
);

CREATE TABLE IF NOT EXISTS metrics.longest_listening_day (
    date DATE,
    play_count INT
);

CREATE TABLE IF NOT EXISTS metrics.top_played_song (
    song_id VARCHAR(255),
    song_name VARCHAR(255),
    artist_id VARCHAR(255),
    artist_name VARCHAR(255),
    artist_image_url VARCHAR(255),
    play_count INT
);