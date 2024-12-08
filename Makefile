include .env

help:
	@echo "## docker-build-arm			- Build Docker Images (arm64) including its inter-container network."
	@echo "## postgres					- Run a Postgres container debezium ready."
	@echo "## spark						- Run a Spark cluster, rebuild the postgres container, then create the destination tables "
	@echo "## airflow					- Spinup airflow scheduler and webserver."
	@echo "## clean						- Cleanup all running containers related to the challenge."

# Building the docker images for arm-based machines
docker-build-arm:
	@echo '__________________________________________________________'
	@echo 'Building All Docker Images ...'
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
	@docker build -t dataeng-dibimbing/debezium -f ./docker/Dockerfile.debezium .
	@echo '==========================================================='

stop-postgres:
	@docker stop ${POSTGRES_CONTAINER_NAME} ${POSTGRES_REPLICA_CONTAINER_NAME} ${POSTGRES_ANALYSIS_CONTAINER_NAME}
stop-spark:
	@docker stop ${SPARK_CONTAINER_NAME}
stop-airflow:
	@docker stop ${AIRFLOW_CONTAINER_NAME}
stop-flask:
	@docker stop ${FLASK_CONTAINER_NAME}
stop-dashboard:
	@docker stop ${DASHBOARD_CONTAINER_NAME}
stop-debezium:
	@docker stop ${DEBEZIUM_CONTAINER_NAME}

docker-build:
	@echo '__________________________________________________________'
	@echo 'Building Single Docker Image ...'
	@echo '__________________________________________________________'
	@if [ "$(service)" = "spark" ]; then \
		docker build -t dataeng-dibimbing/spark -f ./docker/Dockerfile.spark .; \
	elif [ "$(service)" = "airflow" ]; then \
		docker build -t dataeng-dibimbing/airflow -f ./docker/Dockerfile.airflow .; \
	elif [ "$(service)" = "flask" ]; then \
		docker build -t dataeng-dibimbing/flask -f ./docker/Dockerfile.flask .; \
	elif [ "$(service)" = "dashboard" ]; then \
		docker build -t dataeng-dibimbing/dashboard -f ./docker/Dockerfile.dashboard .; \
	elif [ "$(service)" = "debezium" ]; then \
		docker build -t dataeng-dibimbing/debezium -f ./docker/Dockerfile.debezium .; \
	elif [ "$(service)" = "jupyter" ]; then \
		docker build -t dataeng-dibimbing/jupyter -f ./docker/Dockerfile.jupyter .; \
	else \
		echo "Invalid service name. Available services: spark, airflow, flask, dashboard, debezium, jupyter"; \
	fi
	@echo '==========================================================='

# Creating the jupyter instance
jupyter: jupyter-create
jupyter-create:
	@echo '__________________________________________________________'
	@echo 'Creating Jupyter Instance ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-jupyter.yml --env-file .env up -d
	@echo 'Fetching Jupyter token...'
	@sleep 5 # Wait for the container to start
	@docker logs dataeng-jupyter 2>&1 | awk -F'token=' '/token=/ {print $2}' | awk -F' ' '{print $1}' | tail -n1
	@echo '==========================================================='

# Creating the datahub instance
datahub: datahub-create
datahub-create:
	@echo '__________________________________________________________'
	@echo 'Creating Datahub Instance ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-datahub.yml --env-file .env up -d
	@echo '==========================================================='

# Creating the dashboard instance
dashboard: dashboard-create
dashboard-create:
	@echo '__________________________________________________________'
	@echo 'Creating Dashboard Instance ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-dashboard.yml --env-file .env up -d
	@echo '==========================================================='

# Creating the spark cluster instance
spark: spark-create
spark-create:
	@echo '__________________________________________________________'
	@echo 'Creating Spark Cluster ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-spark.yml --env-file .env up -d
	@echo '==========================================================='

# Creating the flask instance
flask: flask-create
flask-create:
	@echo '__________________________________________________________'
	@echo 'Creating Flask Instance ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-flask.yml --env-file .env up -d
	@echo '==========================================================='

# Creating the airflow instance
airflow: airflow-create
airflow-create:
	@echo '__________________________________________________________'
	@echo 'Creating Airflow Instance ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-airflow.yml --env-file .env up -d
	@echo '==========================================================='
	@sleep 10
	@echo 'Airflow websrver is ready to be accessed on http://localhost:${AIRFLOW_WEBSERVER_PORT}'

# Creating the postgres instance
postgres: postgres-create postgres-create-table
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

# Creating the tables in the main postgres
postgres-create-table:
	@echo '__________________________________________________________'
	@echo 'Creating tables in main postgres...'
	@echo '_________________________________________'
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f sql/main_schema_ddl.sql
	@echo '_________________________________________'
	@echo 'Creating publication in main postgres...'
	@echo '_________________________________________'
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f sql/publication.sql
	@echo '==========================================================='
	@echo '__________________________________________________________'
	@echo 'Creating tables in replica postgres...'
	@echo '_________________________________________'
	@docker exec -it ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -f sql/replica_schema_ddl.sql
	@echo '==========================================================='


# Inserting the data into the main postgres
postgres-full-insert: postgres-insert-album postgres-insert-song postgres-insert-artist postgres-insert-history
postgres-insert-album:
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f sql/insert_main_album.sql

postgres-insert-song:
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f sql/insert_main_song.sql

postgres-insert-artist:
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f sql/insert_main_artist.sql

postgres-insert-history:
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f sql/insert_main_history.sql

postgres-truncate-datamart:
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f sql/truncate_analysis.sql

# Connecting to postgres containers
connect-main-postgres:
	@docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
connect-replica-postgres:
	@docker exec -it ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB}
connect-airflow-postgres:
	@docker exec -it ${POSTGRES_AIRFLOW_CONTAINER_NAME} psql -U ${POSTGRES_AIRFLOW_USER} -d ${POSTGRES_AIRFLOW_DB}

# Checking the count comparison between main and replica postgres
postgres-count-check:
	@printf "Table\t\tMain DB\t\tReplica DB\n"
	@printf "%s\n" "----------------------------------------"
	@printf "dim_album\t"
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c 'SELECT COUNT(*) FROM "dim_album";' | tr -d '\n' | xargs printf "%s\t\t"
	@docker exec ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -t -c 'SELECT COUNT(*) FROM "dataeng-postgres_public_dim_album";' | xargs printf "%s\n"
	
	@printf "dim_artist\t"
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c 'SELECT COUNT(*) FROM "dim_artist";' | tr -d '\n' | xargs printf "%s\t\t"
	@docker exec ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -t -c 'SELECT COUNT(*) FROM "dataeng-postgres_public_dim_artist";' | xargs printf "%s\n"
	
	@printf "dim_song\t"
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c 'SELECT COUNT(*) FROM "dim_song";' | tr -d '\n' | xargs printf "%s\t\t"
	@docker exec ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -t -c 'SELECT COUNT(*) FROM "dataeng-postgres_public_dim_song";' | xargs printf "%s\n"
	
	@printf "fact_history\t"
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c 'SELECT COUNT(*) FROM "fact_history";' | tr -d '\n' | xargs printf "%s\t\t"
	@docker exec ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -t -c 'SELECT COUNT(*) FROM "dataeng-postgres_public_fact_history";' | xargs printf "%s\n"

postgres-truncate: postgres-truncate-main postgres-truncate-replica
postgres-truncate-main:
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "dim_album" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "dim_artist" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "dim_song" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "fact_history";'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "analysis.album_completion_analysis" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "analysis.song_duration_preference" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "analysis.explicit_preference" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "analysis.day_of_week_listening_distribution" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "analysis.session_between_songs" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "analysis.song_popularity_distribution" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "analysis.hour_of_day_listening_distribution" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "analysis.album_release_year_play_count" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "metrics.longest_streak_of_top_listened_artist" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "metrics.total_minutes_listened" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "metrics.total_minutes_listened_by_day_of_week" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "metrics.total_songs_played" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "metrics.top_played_songs" CASCADE;'
	@docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c 'TRUNCATE TABLE "metrics.biggest_listening_day" CASCADE;'

postgres-truncate-replica:
	@docker exec ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -c 'TRUNCATE TABLE "dataeng-postgres_public_dim_album" CASCADE;'
	@docker exec ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -c 'TRUNCATE TABLE "dataeng-postgres_public_dim_artist" CASCADE;'
	@docker exec ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -c 'TRUNCATE TABLE "dataeng-postgres_public_dim_song" CASCADE;'
	@docker exec ${POSTGRES_REPLICA_CONTAINER_NAME} psql -U ${POSTGRES_REPLICA_USER} -d ${POSTGRES_REPLICA_DB} -c 'TRUNCATE TABLE "dataeng-postgres_public_fact_history";'

# Debezium related commands
# Creating Debezium instance and topics necessary
debezium: debezium-create debezium-create-topic debezium-register-all
debezium-create:
	@echo '__________________________________________________________'
	@echo 'Creating Debezium Instance ...'
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-debezium.yml --env-file .env up -d
debezium-create-topic:
	@echo 'Waiting for Kafka broker to start...'
	@sleep 10
	@echo 'Creating Kafka Topics ...'
	@docker exec kafka /kafka/bin/kafka-topics.sh --create --if-not-exists --bootstrap-server localhost:9092 --topic dataeng-postgres.public.dim_album --partitions 1 --replication-factor 1
	@docker exec kafka /kafka/bin/kafka-topics.sh --create --if-not-exists --bootstrap-server localhost:9092 --topic dataeng-postgres.public.dim_artist --partitions 1 --replication-factor 1
	@docker exec kafka /kafka/bin/kafka-topics.sh --create --if-not-exists --bootstrap-server localhost:9092 --topic dataeng-postgres.public.dim_song --partitions 1 --replication-factor 1
	@docker exec kafka /kafka/bin/kafka-topics.sh --create --if-not-exists --bootstrap-server localhost:9092 --topic dataeng-postgres.public.fact_history --partitions 1 --replication-factor 1
	@docker exec kafka /kafka/bin/kafka-topics.sh --create --if-not-exists --bootstrap-server localhost:9092 --topic dataeng-postgres.transaction --partitions 1 --replication-factor 1
	@echo '==========================================================='

# Registering the connectors
debezium-register-all: debezium-register-source debezium-register-sink
debezium-register-source:
	@curl -X POST -H "Content-Type: application/json" --data @cdc_connectors/source-connector-config.json http://localhost:8083/connectors
	@echo '__________________________________________________________'
	@echo 'Source Connector Registered'
	@echo '__________________________________________________________'
	@echo 'Source Connector Status'
	@curl -X GET http://localhost:8083/connectors/postgres-source-connector/status
	@echo '==========================================================='
debezium-register-sink:
	@curl -X POST -H "Content-Type: application/json" --data @cdc_connectors/sink-connector-dim-artist-config.json http://localhost:8083/connectors
	@echo 'Registered dim_artist sink connector'
	@curl -X POST -H "Content-Type: application/json" --data @cdc_connectors/sink-connector-dim-album-config.json http://localhost:8083/connectors
	@echo 'Registered dim_album sink connector'
	@curl -X POST -H "Content-Type: application/json" --data @cdc_connectors/sink-connector-dim-song-config.json http://localhost:8083/connectors
	@echo 'Registered dim_song sink connector'
	@curl -X POST -H "Content-Type: application/json" --data @cdc_connectors/sink-connector-fact-history-config.json http://localhost:8083/connectors
	@echo 'Registered fact_history sink connector'
	@echo '__________________________________________________________'
	@echo 'All Sink Connectors Registered'
	@echo '__________________________________________________________'

# Deleting the sink connectors
debezium-delete-sink:
	@curl -X DELETE http://localhost:8083/connectors/jdbc-sink-connector-dim-artist
	@curl -X DELETE http://localhost:8083/connectors/jdbc-sink-connector-dim-album
	@curl -X DELETE http://localhost:8083/connectors/jdbc-sink-connector-dim-song
	@curl -X DELETE http://localhost:8083/connectors/jdbc-sink-connector-fact-history
	@echo '__________________________________________________________'
	@echo 'All Sink Connectors Deleted'
	@echo '__________________________________________________________'

# Checking the status of the connectors
debezium-check-all: debezium-check-source debezium-check-sink
debezium-check-source:
	@echo 'Checking source connector...'
	@curl -X GET http://localhost:8083/connectors/postgres-source-connector/status

debezium-check-sink:
	@echo 'Checking dim_song sink connector...'
	@curl -X GET http://localhost:8083/connectors/jdbc-sink-connector-dim-song/status
	@echo 'Checking dim_artist sink connector...'
	@curl -X GET http://localhost:8083/connectors/jdbc-sink-connector-dim-artist/status
	@echo 'Checking dim_album sink connector...'
	@curl -X GET http://localhost:8083/connectors/jdbc-sink-connector-dim-album/status
	@echo 'Checking fact_history sink connector...'
	@curl -X GET http://localhost:8083/connectors/jdbc-sink-connector-fact-history/status
	@echo ''
	
debezium-check-connectors:
	@curl -X GET http://localhost:8083/connectors
	@echo ''

# Checking the kafka topics
list-kafka-topics:
	@docker exec kafka /kafka/bin/kafka-topics.sh --list --bootstrap-server kafka:9092

# Cleaning up the containers and volumes
clean:
	@docker ps -aq | xargs docker stop
	@docker ps -aq | xargs docker rm -f
	@docker volume ls -q | xargs docker volume rm -f

# Cleaning up the images
clean-images:
	@docker images -q | xargs docker rmi -f

# Stopping the containers
stop-all:
	@docker ps -aq | xargs docker stop

# Connecting to postgres container
postgres-bash:
	@docker exec -it dataeng-postgres bash

# Running the db final project
run-db-final-project: postgres spark debezium flask airflow 

# postgres_db=# insert into dim_artist(artist_id, name, external_url, follower_count, image_url, popularity) VALUES('a', 'a', 'a', 1, 'a', 10);