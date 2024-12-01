include .env

help:
	@echo "## docker-build-arm		- Build Docker Images (arm64) including its inter-container network."
	@echo "## postgres			- Run a Postgres container debezium ready."
	@echo "## spark			- Run a Spark cluster, rebuild the postgres container, then create the destination tables "
	@echo "## airflow			- Spinup airflow scheduler and webserver."
	@echo "## clean			- Cleanup all running containers related to the challenge."

docker-build-arm:
	@echo '__________________________________________________________'
	@echo 'Building Docker Images ...'
	@echo '__________________________________________________________'
	@docker network inspect dataeng-network >/dev/null 2>&1 || docker network create dataeng-network
	@echo '__________________________________________________________'
	@docker build -t dataeng-dibimbing/spark -f ./docker/Dockerfile.spark .
	@echo '__________________________________________________________'
	@docker build -t dataeng-dibimbing/airflow -f ./docker/Dockerfile.airflow .
	@echo '__________________________________________________________'
	@docker build -t dataeng-dibimbing/flask -f ./docker/Dockerfile.flask .
	@echo '==========================================================='
	@docker build -t dataeng-dibimbing/dashboard -f ./docker/Dockerfile.dashboard .
	@echo '==========================================================='

dashboard: dashboard-create
dashboard-create:
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

postgres: postgres-create
postgres-create:
	@docker compose -f ./docker/docker-compose-postgres.yml --env-file .env up -d
	@echo '__________________________________________________________'
	@echo 'Main Postgres container created at port ${POSTGRES_PORT}...'
	@echo '__________________________________________________________'
	@echo 'Main Postgres Docker Host	: ${POSTGRES_CONTAINER_NAME}' &&\
		echo 'Main Postgres Account	: ${POSTGRES_USER}' &&\
		echo 'Main Postgres password	: ${POSTGRES_PASSWORD}' &&\
		echo 'Main Postgres Db		: ${POSTGRES_DB}'
	@echo '__________________________________________________________'
	@echo 'Analysis Postgres container created at port ${POSTGRES_ANALYSIS_PORT}...'
	@echo '__________________________________________________________'
	@echo 'Analysis Postgres Docker Host	: ${POSTGRES_ANALYSIS_CONTAINER_NAME}' &&\
		echo 'Analysis Postgres Account	: ${POSTGRES_ANALYSIS_USER}' &&\
		echo 'Analysis Postgres password	: ${POSTGRES_ANALYSIS_PASSWORD}' &&\
		echo 'Analysis Postgres Db		: ${POSTGRES_ANALYSIS_DB}'
	@echo '__________________________________________________________'
	@echo 'Replica Postgres container created at port ${POSTGRES_REPLICA_PORT}...'
	@echo '__________________________________________________________'
	@echo 'Replica Postgres Docker Host	: ${POSTGRES_REPLICA_CONTAINER_NAME}' &&\
		echo 'Replica Postgres Account	: ${POSTGRES_REPLICA_USER}' &&\
		echo 'Replica Postgres password	: ${POSTGRES_REPLICA_PASSWORD}' &&\
		echo 'Replica Postgres Db		: ${POSTGRES_REPLICA_DB}'
	@echo '__________________________________________________________'
	@echo 'Source Postgres Host	: ${POSTGRES_HOST_SOURCE}' &&\
		echo 'Source Postgres Account	: ${POSTGRES_SOURCE_USER}' &&\
		echo 'Source Postgres password	: ${POSTGRES_SOURCE_PASSWORD}' &&\
		echo 'Source Postgres Db		: ${POSTGRES_SOURCE_DB}'
	@sleep 5
	@echo '==========================================================='

postgres-create-table:
	@echo '__________________________________________________________'
	@echo 'Creating tables in main postgres...'
	@echo '_________________________________________'
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f sql/schema_ddl.sql
	@echo '==========================================================='
	@echo '__________________________________________________________'
	@echo 'Creating tables in replica postgres...'
	@echo '_________________________________________'
	@docker exec -it ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -f sql/schema_ddl.sql
	@echo '==========================================================='

connect-main-postgres:
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

connect-replica-postgres:
	@docker exec -it ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB}

connect-analysis-postgres:
	@docker exec -it ${POSTGRES_ANALYSIS_CONTAINER_NAME} psql -U ${POSTGRES_ANALYSIS_USER} -d ${POSTGRES_ANALYSIS_DB}

clean:
	@bash ./scripts/goodnight.sh

stop:
	@docker ps --filter name=dataeng* -aq | xargs docker stop

postgres-bash:
	@docker exec -it dataeng-postgres bash

run-db-final-project: postgres-create && sleep 5 && flask-create && airflow-create && spark-create