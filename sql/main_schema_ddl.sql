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

CREATE SEQUENCE IF NOT EXISTS analysis_album_completion_analysis_id_seq;

CREATE TABLE IF NOT EXISTS analysis.album_completion_analysis (
    id INTEGER PRIMARY KEY DEFAULT nextval('analysis_album_completion_analysis_id_seq'),
    album_title VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    album_image_url VARCHAR(255) NOT NULL,
    total_tracks INT NOT NULL,
    unique_tracks_played INT NOT NULL,
    completion_percentage FLOAT NOT NULL,
    listening_status VARCHAR(255) NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS analysis_song_duration_preference_id_seq;

CREATE TABLE IF NOT EXISTS analysis.song_duration_preference (
    id INTEGER PRIMARY KEY DEFAULT nextval('analysis_song_duration_preference_id_seq'),
    duration_category VARCHAR(255) NOT NULL,
    play_count INT NOT NULL,
    percentage FLOAT NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS analysis_explicit_preference_id_seq;

CREATE TABLE IF NOT EXISTS analysis.explicit_preference (
    id INTEGER PRIMARY KEY DEFAULT nextval('analysis_explicit_preference_id_seq'),
    explicit BOOLEAN NOT NULL,
    play_count INT NOT NULL,
    percentage FLOAT NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS analysis_day_of_week_listening_distribution_id_seq;

CREATE TABLE IF NOT EXISTS analysis.day_of_week_listening_distribution (
    id INTEGER PRIMARY KEY DEFAULT nextval('analysis_day_of_week_listening_distribution_id_seq'),
    day_of_week VARCHAR(255) NOT NULL,
    play_count INT NOT NULL,
    unique_songs INT NOT NULL,
    unique_artists INT NOT NULL,
    song_variety_percentage FLOAT NOT NULL,
    artist_variety_percentage FLOAT NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS analysis_session_between_songs_id_seq;

CREATE TABLE IF NOT EXISTS analysis.session_between_songs (
    id INTEGER PRIMARY KEY DEFAULT nextval('analysis_session_between_songs_id_seq'),
    session_type VARCHAR(255) NOT NULL,
    count INT NOT NULL,
    percentage FLOAT NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS analysis_song_popularity_distribution_id_seq;

CREATE TABLE IF NOT EXISTS analysis.song_popularity_distribution (
    id INTEGER PRIMARY KEY DEFAULT nextval('analysis_song_popularity_distribution_id_seq'),
    popularity_bracket INT NOT NULL,
    play_count INT NOT NULL,
    popularity_range VARCHAR(10) NOT NULL,
    percentage FLOAT NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS analysis_hour_of_day_listening_distribution_id_seq;

CREATE TABLE IF NOT EXISTS analysis.hour_of_day_listening_distribution (
    id INTEGER PRIMARY KEY DEFAULT nextval('analysis_hour_of_day_listening_distribution_id_seq'),
    hour_of_day INT NOT NULL,
    play_count INT NOT NULL,
    percentage FLOAT NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS analysis_album_release_year_play_count_id_seq;

CREATE TABLE IF NOT EXISTS analysis.album_release_year_play_count (
    id INTEGER PRIMARY KEY DEFAULT nextval('analysis_album_release_year_play_count_id_seq'),
    release_year INT NOT NULL,
    play_count INT NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS metrics_statistics_id_seq;

CREATE TABLE IF NOT EXISTS metrics.statistics (
    id INTEGER PRIMARY KEY DEFAULT nextval('metrics_statistics_id_seq'),
    total_miliseconds BIGINT NOT NULL,
    total_songs_played INT NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS metrics_artist_longest_streak_id_seq;

CREATE TABLE IF NOT EXISTS metrics.artist_longest_streak (
    id INTEGER PRIMARY KEY DEFAULT nextval('metrics_artist_longest_streak_id_seq'),
    artist_id VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    artist_image_url VARCHAR(255) NOT NULL,
    streak_days INT NOT NULL,
    date_from DATE NOT NULL,
    date_until DATE NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS metrics_longest_listening_day_id_seq;

CREATE TABLE IF NOT EXISTS metrics.longest_listening_day (
    id INTEGER PRIMARY KEY DEFAULT nextval('metrics_longest_listening_day_id_seq'),
    date DATE NOT NULL,
    total_miliseconds BIGINT NOT NULL,
    songs_played INT NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS metrics_top_played_song_id_seq;

CREATE TABLE IF NOT EXISTS metrics.top_played_song (
    id INTEGER PRIMARY KEY DEFAULT nextval('metrics_top_played_song_id_seq'),
    song_id VARCHAR(255) NOT NULL,
    song_title VARCHAR(255) NOT NULL,
    artist_id VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    artist_image_url VARCHAR(255) NOT NULL,
    play_count INT NOT NULL,
    first_played_at DATE NOT NULL,
    last_played_at DATE NOT NULL
);