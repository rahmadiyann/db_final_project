#!/bin/bash

# Check if any tables were provided as arguments
if [ $# -eq 0 ]; then
    echo "Error: No tables specified"
    echo "Usage: $0 table1 table2 ..."
    exit 1
fi

# Loop through each table name provided as argument
for TABLE_NAME in "$@"
do
    echo "Dumping table ${TABLE_NAME}"
    PGPASSWORD=${POSTGRES_SOURCE_PASSWORD} pg_dump --data-only --rows-per-insert=100 -h ${POSTGRES_HOST_SOURCE} -U ${POSTGRES_SOURCE_USER} -d ${POSTGRES_SOURCE_DB} -t ${TABLE_NAME} > /opt/airflow/data/${TABLE_NAME}.sql
done
echo "Dump completed"