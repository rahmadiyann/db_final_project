#!/bin/bash

echo "Truncating analysis tables..."
PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_CONTAINER_NAME} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /sql/truncate_analysis.sql
echo "Truncate completed"
