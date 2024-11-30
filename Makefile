include .env

help:
	@echo "## docker-build-arm		- Build Docker Images (arm64) including its inter-container network."
	@echo "## postgres			- Run a Postgres container  "
	@echo "## spark			- Run a Spark cluster, rebuild the postgres container, then create the destination tables "
	@echo "## airflow			- Spinup airflow scheduler and webserver."
	@echo "## kafka			- Spinup kafka cluster (Kafka+Zookeeper)."
	@echo "## clean			- Cleanup all running containers related to the challenge."

docker-build-arm:
	@echo '__________________________________________________________'
	@echo 'Building Docker Images ...'
	@echo '__________________________________________________________'
	@docker network inspect dataeng-network >/dev/null 2>&1 || docker network create dataeng-network
	@echo '__________________________________________________________'
	@docker build -t dataeng-dibimbing/spark -f ./docker/Dockerfile.spark .
	@echo '__________________________________________________________'
	@docker build -t dataeng-dibimbing/airflow -f ./docker/Dockerfile.airflow-arm .
	@echo '__________________________________________________________'
	@docker build -t dataeng-dibimbing/jupyter -f ./docker/Dockerfile.jupyter .
	@echo '==========================================================='
	@docker build -t dataeng-dibimbing/flask -f ./docker/Dockerfile.flask .
	@echo '==========================================================='
	@docker build -t dataeng-dibimbing/dashboard -f ./docker/Dockerfile.dashboard .
	@echo '==========================================================='

dashboard:
	@echo '__________________________________________________________'
	@echo 'Creating Dashboard Instance ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-dashboard.yml --env-file .env up -d
	@echo '==========================================================='


spark: spark-create
spark-create:
	@echo '__________________________________________________________'
	@echo 'Creating Spark Cluster ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-spark.yml --env-file .env up -d
	@echo '==========================================================='

flask: flask-create

flask-create:
	@echo '__________________________________________________________'
	@echo 'Creating Flask Instance ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-flask.yml --env-file .env up -d
	@echo '==========================================================='

airflow: airflow-create
airflow-create:
	@echo '__________________________________________________________'
	@echo 'Creating Airflow Instance ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-airflow.yml --env-file .env up
	@echo '==========================================================='

postgres: postgres-create postgres-create-warehouse postgres-create-table postgres-ingest-csv

postgres-create:
	@docker compose -f ./docker/docker-compose-postgres.yml --env-file .env up -d
	@echo '__________________________________________________________'
	@echo 'Postgres container created at port ${POSTGRES_PORT}...'
	@echo '__________________________________________________________'
	@echo 'Main Postgres Docker Host	: ${POSTGRES_CONTAINER_NAME}' &&\
		echo 'Main Postgres Account	: ${POSTGRES_USER}' &&\
		echo 'Main Postgres password	: ${POSTGRES_PASSWORD}' &&\
		echo 'Main Postgres Db		: ${POSTGRES_DB}'
	@echo '__________________________________________________________'
	@echo 'Source Postgres Host	: ${POSTGRES_HOST_SOURCE}' &&\
		echo 'Source Postgres Account	: ${POSTGRES_SOURCE_USER}' &&\
		echo 'Source Postgres password	: ${POSTGRES_SOURCE_PASSWORD}' &&\
		echo 'Source Postgres Db		: ${POSTGRES_SOURCE_DB}'
	@echo '__________________________________________________________'
	@echo 'Analysis Postgres Docker Host	: ${POSTGRES_CONTAINER_NAME}-analysis' &&\
		echo 'Analysis Postgres Account	: ${POSTGRES_USER}' &&\
		echo 'Analysis Postgres password	: ${POSTGRES_PASSWORD}' &&\
		echo 'Analysis Postgres Db		: ${POSTGRES_DB}-analysis'
	@sleep 5
	@echo '==========================================================='

kafka: kafka-create

kafka-create:
	@echo '__________________________________________________________'
	@echo 'Creating Kafka Cluster ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-kafka.yml --env-file .env up -d
	@echo 'Waiting for uptime on http://localhost:8083 ...'
	@sleep 20
	@echo '==========================================================='

clean:
	@bash ./scripts/goodnight.sh

stop:
	@docker ps --filter name=dataeng* -aq | xargs docker stop

postgres-bash:
	@docker exec -it dataeng-postgres bash

run-db-final-project: postgres-create flask-create airflow-create spark-create
