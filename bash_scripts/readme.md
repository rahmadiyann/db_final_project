# Bash Scripts

This directory contains various bash scripts used in the data pipeline.

## Scripts

### `api_extraction.sh`

This script makes an API call to extract recent played data. It takes the following arguments:

- `timestamp`: The timestamp in milliseconds of the last fetch time
- `dir_path`: The output directory path to save the response
- `file_name`: The name of the JSON file to save the response to

### `data_dump.sh`

This script dumps specified PostgreSQL tables to SQL files. It takes one or more table names as arguments.

The dump files are saved in the `/sql/migration/` directory with the naming format `<table_name>.sql`.

### `data_load.sh`

This script loads data from SQL dump files into specified PostgreSQL tables. It takes one or more table names as arguments.

The script looks for the dump files in the `/sql/migration/` directory with the naming format `<table_name>.sql`.

### `truncate_table.sh`

This script truncates the analysis tables in the PostgreSQL database. It runs the SQL commands in the `/sql/truncate_analysis.sql` file.

## Usage

Make sure to set the required environment variables before running these scripts:

- `POSTGRES_HOST_SOURCE`: The hostname of the source PostgreSQL database
- `POSTGRES_SOURCE_DB`: The name of the source PostgreSQL database
- `POSTGRES_SOURCE_USER`: The username for the source PostgreSQL database
- `POSTGRES_SOURCE_PASSWORD`: The password for the source PostgreSQL database
- `POSTGRES_CONTAINER_NAME`: The name of the PostgreSQL container
- `POSTGRES_DB`: The name of the PostgreSQL database
- `POSTGRES_USER`: The username for the PostgreSQL database
- `POSTGRES_PASSWORD`: The password for the PostgreSQL database

Run the scripts by providing the necessary arguments. For example:

```bash
./api_extraction.sh 1625097600000 /path/to/output response.json
./data_dump.sh table1 table2
./data_load.sh table1 table2
./truncate_table.sh
```
