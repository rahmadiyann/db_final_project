# Spotify Data Pipeline and Analytics Platform

This project is an end-to-end data pipeline and analytics platform for Spotify listening data. It includes data ingestion, transformation, storage, and visualization components, providing a comprehensive solution for analyzing and deriving insights from Spotify user data.

## Architecture Overview

The project architecture consists of the following main components:

1. **Data Ingestion**:

   - Spotify API: Fetches user listening data using the Spotify API.
   - Flask Endpoint: Exposes endpoints to retrieve Spotify access token and Spotify listening history data.

2. **Data Storage**:

   - Source Database (PostgreSQL): Stores raw data from the Spotify API.
   - Main Database (PostgreSQL): Stores transformed data for analysis and serves as the data source for the dashboard.
   - Replica Database (PostgreSQL): Stores CDC data for the main database.

3. **Data Pipeline**:

   - Apache Airflow: Orchestrates the data pipeline tasks and manages the workflow.
   - Apache Spark: Performs data transformations and aggregations using PySpark.
   - Debezium: Implements Change Data Capture (CDC) to synchronize data between the main and replica databases.

4. **Data Quality and Testing**:

   - Soda Core: Performs data quality checks and validations on the transformed data.

5. **Data Visualization**:
   - Next.js Dashboard: Provides a web-based interface to visualize and explore the analyzed Spotify data.

## Setup and Configuration

1. Clone the repository:

   ```
   git clone https://github.com/rahmadiyann/db-final-project.git
   ```

2. Set up the required environment variables in the `.env` file. Refer to the `.env.example` file for the necessary variables.

3. Build and start the Docker containers:

   ```
   make docker-build-arm
   make postgres
   make spark
   make debezium
   make flask
   make airflow
   make dashboard
   ```

4. Access the following services:
   - Airflow Web UI: `http://localhost:8081`
   - Spark Master UI: `http://localhost:8100`
   - Next.js Dashboard: `http://localhost:3000`
   - Flask Endpoint and Spotify Auth: `http://localhost:8000`

## Data Pipeline

The data pipeline is orchestrated using Apache Airflow and consists of the following main stages:

1. **Data Ingestion**:

   - The `flask_to_main_hourly` DAG fetches listening data from the Spotify API using the Flask endpoint and stores it in the source database.

2. **Data Transformation**:

   - The `spotify_analysis_etl` DAG performs the following tasks:
     - Extracts data from the source database.
     - Transforms the data using Apache Spark (PySpark) scripts in the `spark_scripts` directory.
     - Loads the transformed data into the main database.
   - The transformations include aggregations, feature engineering, and data cleaning.

3. **Data Quality Checks**:

   - The `flask_to_main_hourly` and `spotify_analysis_etl` DAG includes data quality checks using Soda Core.
   - The checks are defined in the `soda/checks` directory and ensure the integrity and validity of the transformed data.

4. **Change Data Capture (CDC)**:

   - Debezium is used to capture changes in the source database and synchronize them with the main database.
   - The CDC configuration files are located in the `cdc_connectors` directory.

5. **Data Visualization**:
   - The Next.js dashboard in the `dashboard` directory fetches data from the main database and provides visualizations and insights.

## Spark Transformations

The Spark transformations are implemented using PySpark and are located in the `spark_scripts/transformations` directory. Each transformation script focuses on a specific aspect of the data, such as:

- Album completion rate
- Artist listening streaks
- Listening preferences
- Popularity distribution
- Session analysis

The transformations are executed as part of the `spotify_analysis_etl` DAG in Airflow.

## Flask Endpoint

The Flask endpoint in the `flask_endpoint` directory exposes APIs to interact with the Spotify API and obtain access token as well as retrieve user listening data. It handles authentication, data retrieval, and storage in the main database.

## Dashboard

The Next.js dashboard in the `dashboard` directory provides a web-based interface to visualize and explore the analyzed Spotify data. It fetches data from the main database and renders interactive charts and insights.

## Makefile

The `Makefile` contains useful commands for building, starting, and managing the project components. Some key commands include:

- `make docker-build-arm`: Builds the Docker images for the project components.
- `make postgres`: Starts the PostgreSQL containers for the source and main databases.
- `make debezium`: Starts the Debezium CDC connector.
- `make flask`: Starts the Flask endpoint.
- `make spark`: Starts the Apache Spark cluster.
- `make airflow`: Starts the Airflow scheduler and web server.
- `make dashboard`: Starts the Next.js dashboard.
- `make clean`: Cleans up the running containers and volumes.

Refer to the Makefile for more available commands.

## Conclusion

This project provides a robust and scalable solution for ingesting, processing, and analyzing Spotify listening data. By leveraging Apache Airflow, Apache Spark, Debezium, and Soda Core, it ensures data quality, reliability, and efficient processing. The Next.js dashboard offers an intuitive interface to explore and derive insights from the analyzed data.

Feel free to explore the codebase and adapt it to your specific requirements. Happy analyzing!
