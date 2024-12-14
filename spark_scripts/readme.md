# Spark ETL Scripts

This directory contains the Spark ETL scripts for processing and transforming data in the Spotify data pipeline.

## Scripts

### `run_etl.py`

The main script that orchestrates the ETL process. It takes command-line arguments to specify the source stage, destination stage, table name, and whether to apply transformations.

Usage:

```bash
python run_etl.py --stage <source_stage> --destination <destination_stage> --table <table_name> [--transform]
```

- `<source_stage>`: The source stage of the data (source, landing, staging).
- `<destination_stage>`: The destination stage for the transformed data (landing, staging, datamart, hist).
- `<table_name>`: The name of the table to process.
- `--transform`: Optional flag to indicate whether to apply transformations.

### Transformations

The `transformations` directory contains the ETL classes for specific transformations:

- `album_completion_rate.py`: Calculates album completion rates.
- `album_release_year_play_count.py`: Calculates play counts by album release year.
- `artist_longest_streak.py`: Determines the artist with the longest listening streak.
- `day_of_week.py`: Calculates listening distribution by day of the week.
- `explicit_pref.py`: Calculates explicit content preference.
- `hour_of_day_play_count.py`: Calculates play counts by hour of the day.
- `longest_listening_day.py`: Determines the longest listening day.
- `popularity_pref.py`: Calculates song popularity preference.
- `session_between_songs.py`: Analyzes session types between songs.
- `song_dur_pref.py`: Calculates song duration preference.
- `statistics.py`: Calculates overall listening statistics.
- `top_played_song_detail.py`: Determines the top played song details.

Each transformation class inherits from the `SparkETLBase` class defined in `utils/etl_base.py` and implements the `transform` method to apply the specific transformation logic.

### Utils

The `utils` directory contains utility modules for the ETL process:

- `etl_base.py`: Defines the base `SparkETLBase` class that provides common functionality for reading source data, writing transformed data, and running the ETL process.
- `spark_helper.py`: Provides helper functions for creating Spark sessions, loading tables, writing data in various formats (CSV, Parquet, JDBC), and reading data from specific paths.

## Usage

To run a specific ETL transformation, use the `run_etl.py` script with the appropriate arguments. For example:

```bash
python run_etl.py --stage landing --destination datamart --table analysis.album_completion_analysis --transform
```

This command will run the ETL process for the `album_completion_analysis` table, reading data from the landing stage, applying transformations, and writing the transformed data to the datamart.

Make sure to have the necessary dependencies installed and the Spark environment properly configured before running the ETL scripts.

## Dependencies

The ETL scripts require the following dependencies:

- PySpark
- PostgreSQL JDBC driver

Make sure to include the PostgreSQL JDBC driver JAR file in the Spark classpath or specify it using the `--jars` option when submitting the Spark job.

## Configuration

The ETL scripts use environment variables to configure the database connection details. Make sure to set the appropriate values in the `.env` file or in the environment where the scripts are executed.

## Logging

The ETL scripts use the Python logging module to log information and errors. The log messages are printed to the console by default. You can modify the logging configuration in the `etl_base.py` module to change the log level or add file-based logging if needed.
