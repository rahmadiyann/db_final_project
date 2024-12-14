# CDC Connectors

This directory contains the configuration files for the Kafka Connect source and sink connectors used in the Change Data Capture (CDC) pipeline.

## Source Connector

The source connector is configured using the `source-connector-config.json` file. It uses the Debezium PostgreSQL connector to capture changes from a PostgreSQL database.

Key configuration properties:

- `connector.class`: The Java class for the Debezium PostgreSQL connector
- `database.hostname`: The hostname of the source PostgreSQL database
- `database.user`: The username for connecting to the source database
- `database.password`: The password for connecting to the source database
- `database.dbname`: The name of the source database
- `table.include.list`: The tables to capture changes from (using a regular expression)
- `plugin.name`: The logical decoding plugin used (pgoutput)
- `slot.name`: The name of the replication slot
- `publication.name`: The name of the publication
- `topic.prefix`: The prefix for the Kafka topics

## Sink Connectors

The sink connectors are configured using the `sink-connector-*-config.json` files. They use the Debezium JDBC sink connector to write the captured changes to a target PostgreSQL database.

There are separate configuration files for each target table:

- `sink-connector-dim-album-config.json`: Writes to the `dim_album` table
- `sink-connector-dim-artist-config.json`: Writes to the `dim_artist` table
- `sink-connector-dim-song-config.json`: Writes to the `dim_song` table
- `sink-connector-fact-history-config.json`: Writes to the `fact_history` table

Key configuration properties:

- `connector.class`: The Java class for the Debezium JDBC sink connector
- `topics.regex`: The regular expression for the source Kafka topics
- `connection.url`: The JDBC URL for the target PostgreSQL database
- `connection.username`: The username for connecting to the target database
- `connection.password`: The password for connecting to the target database
- `insert.mode`: The insertion mode (upsert)
- `primary.key.mode`: The mode for determining the primary key (record_value)
- `primary.key.fields`: The comma-separated list of primary key fields
- `table.name.format`: The format for the target table name
- `errors.tolerance`: The tolerance for errors (all)
- `errors.deadletterqueue.topic.name`: The name of the dead letter queue topic for failed records

## Usage

1. Configure the source and sink connectors by modifying the respective configuration files.

2. Deploy the connectors to the Kafka Connect cluster by submitting the configuration files using the Kafka Connect REST API or a tool like `kafka-connect-cli`.

3. Monitor the status and logs of the connectors to ensure they are running correctly and capturing changes as expected.

Note: Make sure to set the appropriate values for the database connection properties, such as the hostname, username, and password, in the configuration files before deploying the connectors.
