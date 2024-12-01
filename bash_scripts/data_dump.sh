#!/bin/bash

# Array of tables to dump
tables=("fact_history" "dim_album" "dim_song" "dim_artist")

# Loop through each table for dumping
for TABLE_NAME in "${tables[@]}"
do
    echo "Dumping table ${TABLE_NAME}"
    PGPASSWORD=${POSTGRES_SOURCE_PASSWORD} pg_dump --data-only --column-inserts -h ${POSTGRES_HOST_SOURCE} -U ${POSTGRES_SOURCE_USER} -d ${POSTGRES_SOURCE_DB} -t ${TABLE_NAME} > ../data/${TABLE_NAME}.sql
done
echo "Dump completed"