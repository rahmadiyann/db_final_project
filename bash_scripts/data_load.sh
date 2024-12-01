#!/bin/bash

# Array of tables to dump
tables=("fact_history" "dim_album" "dim_song" "dim_artist")

# Loop through each table for loading
for TABLE_NAME in "${tables[@]}"
do
    echo "Loading table ${TABLE_NAME}"
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_CONTAINER_NAME} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f ../data/${TABLE_NAME}.sql
done
echo "Load completed"