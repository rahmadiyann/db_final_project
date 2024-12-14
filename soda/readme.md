# Soda SQL Data Quality Checks

This directory contains the configuration files and data quality checks for Soda SQL, a data quality testing tool.

## Configuration

The `config` directory contains the configuration files for connecting to the PostgreSQL databases:

- `soda_config.yml`: Configuration for connecting to the main database.
- `soda_config_analysis.yml`: Configuration for connecting to the analysis schema in the main database.
- `soda_config_metrics.yml`: Configuration for connecting to the metrics schema in the main database.

The configuration files use environment variables to set the database connection details. Make sure to set the appropriate values in the `.env` file.

## Checks

The `checks` directory contains the data quality check definitions for various tables in the pipeline.

### `source2main` Checks

- `source2main_checks.yml`: Data quality checks for the `fact_history` and dimension tables in the main database.
- `source2main_fact_checks.yml`: Additional data quality checks specifically for the `fact_history` table.

### `spotify_etl` Checks

The `spotify_etl` directory contains data quality checks for the tables in the analysis and metrics schemas.

- `analysis`: Data quality checks for tables in the analysis schema, such as `album_completion_analysis`, `album_release_year_play_count`, `day_of_week_listening_distribution`, etc.
- `metrics`: Data quality checks for tables in the metrics schema, such as `artist_longest_streak`, `longest_listening_day`, `statistics`, `top_played_song`, etc.

## Usage

To run the data quality checks, use the Soda SQL command-line interface (CLI) and specify the appropriate configuration file and checks file.

For example, to run the checks for the `source2main` tables:

```bash
soda run -c soda/config/soda_config.yml -d soda/checks/source2main_checks.yml
```

To run the checks for the analysis tables:

```bash
soda run -c soda/config/soda_config_analysis.yml -d soda/checks/spotify_etl/analysis/
```

Make sure to have Soda SQL installed and properly configured before running the checks.

## Documentation

For more information on how to define data quality checks and use Soda SQL, refer to the [Soda SQL documentation](https://docs.soda.io/soda-sql/overview.html).
