#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Check if any tables were provided as arguments
if [ $# -eq 0 ]; then
    echo "Error: No tables specified"
    echo "Usage: $0 table1 table2 ..."
    exit 1
fi

# Loop through each table for loading
for TABLE_NAME in "$@"
do
    echo "Loading table ${TABLE_NAME}"
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_CONTAINER_NAME} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /sql/migration/${TABLE_NAME}.sql

    # Check if the last command was successful
    if [ $? -ne 0 ]; then
        echo "Error occurred while loading table ${TABLE_NAME}"
        exit 1
    fi
done

echo "Load completed"