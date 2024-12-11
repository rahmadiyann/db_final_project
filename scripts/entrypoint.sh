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

airflow variables set 'email_config' \
-v '{"EMAIL_SENDER": "'$EMAIL_SENDER'", "EMAIL_PASSWORD": '$EMAIL_PASSWORD'}'

airflow variables set 'last_fetch_time' \
-v '0'

airflow variables set 'email_recipient' \
-v '{{"EMAIL_RECIPIENT": "'$EMAIL_RECIPIENT'"}}'

airflow connections add 'email_alert' \
--conn-type 'email' \
--conn-host 'smtp.gmail.com' \
--conn-login $EMAIL_SENDER \
--conn-password $EMAIL_PASSWORD \
--conn-port 587 

export SPARK_FULL_HOST_NAME="spark://$SPARK_MASTER_HOST_NAME"
airflow connections add 'spark_main' \
--conn-type 'spark' \
--conn-host $SPARK_FULL_HOST_NAME \
--conn-port $SPARK_MASTER_PORT
airflow webserver
