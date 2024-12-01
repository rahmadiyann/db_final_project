#!/bin/bash
airflow db init
echo "AUTH_ROLE_PUBLIC = 'Admin'" >> webserver_config.py
airflow connections add 'source_postgres' \
--conn-type 'postgres' \
--conn-login $POSTGRES_SOURCE_USER \
--conn-password $POSTGRES_SOURCE_PASSWORD \
--conn-host $POSTGRES_HOST_SOURCE \
--conn-port $POSTGRES_PORT_SOURCE \
--conn-schema $POSTGRES_SOURCE_DB
airflow connections add 'main_postgres' \
--conn-type 'postgres' \
--conn-login $POSTGRES_USER \
--conn-password $POSTGRES_PASSWORD \
--conn-host $POSTGRES_CONTAINER_NAME \
--conn-port $POSTGRES_PORT \
--conn-schema $POSTGRES_DB
airflow connections add 'analysis_postgres' \
--conn-type 'postgres' \
--conn-login $POSTGRES_USER \
--conn-password $POSTGRES_PASSWORD \
--conn-host $POSTGRES_ANALYSIS_CONTAINER_NAME \
--conn-port $POSTGRES_ANALYSIS_PORT \
--conn-schema $POSTGRES_DB
airflow variables set 'email_config' \
--value '{"EMAIL_SENDER": "'$EMAIL_SENDER'", "EMAIL_PASSWORD": '$EMAIL_PASSWORD'}'

airflow variables set 'email_recipient' \
--value '{{"EMAIL_RECIPIENT": "'$EMAIL_RECIPIENT'"}}'

export SPARK_FULL_HOST_NAME="spark://$SPARK_MASTER_HOST_NAME"
airflow connections add 'spark_main' \
--conn-type 'spark' \
--conn-host $SPARK_FULL_HOST_NAME \
--conn-port $SPARK_MASTER_PORT
airflow webserver
