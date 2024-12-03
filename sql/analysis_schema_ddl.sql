
CREATE TABLE IF NOT EXISTS album_completion_analysis (
    album_title VARCHAR(255),
    artist_name VARCHAR(255),
    total_tracks INT,
    unique_tracks_played INT,
    completion_percentage FLOAT,
    listening_status VARCHAR(255)
) TRUNCATE TABLE;

CREATE TABLE IF NOT EXISTS song_duration_preference (
    duration_category VARCHAR(255),
    play_count INT,
    percentage FLOAT
) TRUNCATE TABLE;

CREATE TABLE IF NOT EXISTS explicit_preference (
    explicit_status VARCHAR(255),
    play_count INT,
    percentage FLOAT
) TRUNCATE TABLE;

CREATE TABLE IF NOT EXISTS seasonal_listening_analysis (
    month VARCHAR(255),
    play_count INT,
    unique_songs INT,
    unique_artists INT,
    song_variety_percentage FLOAT,
    artist_variety_percentage FLOAT
) TRUNCATE TABLE;

CREATE TABLE IF NOT EXISTS session_between_songs (
    session_type VARCHAR(255),
    count INT,
    percentage FLOAT
) TRUNCATE TABLE;

CREATE TABLE IF NOT EXISTS song_popularity_distribution (
    popularity_bracket INT,
    popularity_range VARCHAR(255),
    play_count INT,
    percentage FLOAT
) TRUNCATE TABLE;

CREATE TABLE IF NOT EXISTS hour_of_day_listening_distribution (
    hour_of_day INT,
    play_count INT,
    percentage FLOAT
) TRUNCATE TABLE;

CREATE TABLE IF NOT EXISTS album_release_year_play_count (
    release_year INT,
    play_count INT
) TRUNCATE TABLE;