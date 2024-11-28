#!/bin/bash
airflow db init
echo "AUTH_ROLE_PUBLIC = 'Admin'" >> webserver_config.py
airflow connections add 'postgres_source' \
--conn-type 'postgres' \
--conn-login $POSTGRES_SOURCE_USER \
--conn-password $POSTGRES_SOURCE_PASSWORD \
--conn-host $POSTGRES_HOST_SOURCE \
--conn-port $POSTGRES_PORT_SOURCE \
--conn-schema $POSTGRES_SOURCE_DB
airflow connections add 'postgres_target' \
--conn-type 'postgres' \
--conn-login $POSTGRES_USER \
--conn-password $POSTGRES_PASSWORD \
--conn-host $POSTGRES_CONTAINER_NAME \
--conn-port $POSTGRES_PORT \
--conn-schema $POSTGRES_DB
airflow variables set 'source_params' \
'{"host": "'$POSTGRES_HOST_SOURCE'", "port": '$POSTGRES_PORT_SOURCE', "user": "'$POSTGRES_SOURCE_USER'", "password": "'$POSTGRES_SOURCE_PASSWORD'", "database": "'$POSTGRES_SOURCE_DB'"}'
airflow variables set 'target_params' \
'{"host": "'$POSTGRES_CONTAINER_NAME'", "port": '$POSTGRES_PORT', "user": "'$POSTGRES_USER'", "password": "'$POSTGRES_PASSWORD'", "database": "'$POSTGRES_DB'"}'
export SPARK_FULL_HOST_NAME="spark://$SPARK_MASTER_HOST_NAME"
airflow connections add 'spark_main' \
--conn-type 'spark' \
--conn-host $SPARK_FULL_HOST_NAME \
--conn-port $SPARK_MASTER_PORT
airflow webserver
