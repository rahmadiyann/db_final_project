# Docker Configuration

This directory contains the Docker configuration files for the various services used in the data engineering pipeline.

## Services

### Airflow

- `Dockerfile.airflow`: Dockerfile for building the Airflow image
- `docker-compose-airflow.yml`: Docker Compose file for running Airflow services (webserver and scheduler)

### Dashboard

- `Dockerfile.dashboard`: Dockerfile for building the Next.js dashboard image
- `docker-compose-dashboard.yml`: Docker Compose file for running the dashboard service

### Debezium

- `Dockerfile.debezium`: Dockerfile for building the Debezium image with PostgreSQL JDBC driver and connector
- `docker-compose-debezium.yml`: Docker Compose file for running Debezium services (Zookeeper, Kafka, Kafka Connect, Kafka UI, ksqlDB)

### Flask

- `Dockerfile.flask`: Dockerfile for building the Flask API image
- `docker-compose-flask.yml`: Docker Compose file for running the Flask service

### Jupyter

- `Dockerfile.jupyter`: Dockerfile for building the Jupyter Notebook image with PySpark and additional dependencies
- `docker-compose-jupyter.yml`: Docker Compose file for running the Jupyter service

### PostgreSQL

- `docker-compose-postgres.yml`: Docker Compose file for running PostgreSQL services (main, replica, and Airflow)

### Spark

- `Dockerfile.spark`: Dockerfile for building the Spark image with additional dependencies and JARs
- `docker-compose-spark.yml`: Docker Compose file for running Spark services (master and worker)

## Environment Variables

The Docker Compose files use environment variables defined in the `../.env` file. Make sure to set the appropriate values in the `.env` file before running the services.

## Network

All services are connected to a common Docker network named `dataeng-network`. This network is created as an external network and should be created before running the services.

## Usage

To start a specific service, navigate to the root directory of the project and run:

```bash
docker-compose -f docker/docker-compose-<service>.yml up -d
```

Replace `<service>` with the name of the service you want to start (e.g., `airflow`, `dashboard`, `debezium`, etc.).

To stop a service, run:

```bash
docker-compose -f docker/docker-compose-<service>.yml down
```

Make sure to build the Docker images before starting the services if any changes have been made to the Dockerfiles or if running for the first time.

## Customization

If you need to customize the Docker configurations, you can modify the respective Dockerfile or Docker Compose file for the service. Be cautious when making changes, as it may impact the functionality of the pipeline.
