# spark_utils.py
from pyspark.sql import SparkSession
from datetime import datetime, timedelta
import os

def create_spark_session(app_name):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars", "/opt/jars/pg_jdbc.jar") \
        .getOrCreate()

def get_main_db_properties():
    return {
        'url': f"jdbc:postgresql://{os.getenv('POSTGRES_HOST_SOURCE')}:{os.getenv('POSTGRES_PORT_SOURCE')}/{os.getenv('POSTGRES_SOURCE_DB')}",
        'host': os.getenv('POSTGRES_HOST_SOURCE'),
        'port': os.getenv('POSTGRES_PORT_SOURCE'),
        'database': os.getenv('POSTGRES_SOURCE_DB'),
        'user': os.getenv('POSTGRES_SOURCE_USER'),
        'password': os.getenv('POSTGRES_SOURCE_PASSWORD')
    }
    
def get_analysis_db_properties():
    return {
        'url': f"jdbc:postgresql://{os.getenv('POSTGRES_CONTAINER_NAME').replace('dataeng-postgres', 'dataeng-postgres-analysis')}:{os.getenv('POSTGRES_PORT_ANALYSIS')}/{os.getenv('POSTGRES_DB').replace('postgres_db', 'postgres_db-analysis')}",
        'host': os.getenv('POSTGRES_CONTAINER_NAME').replace("dataeng-postgres", "dataeng-postgres-analysis"),
        'port': os.getenv('POSTGRES_PORT_ANALYSIS'),
        'database': os.getenv('POSTGRES_DB').replace("postgres_db", "postgres_db-analysis"),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }

def load_table(spark, table_name, db_properties):
    jdbc_url = f"jdbc:postgresql://{db_properties['host']}:{db_properties['port']}/{db_properties['database']}"
    
    return spark.read \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", table_name) \
        .option("user", db_properties['user']) \
        .option("password", db_properties['password']) \
        .option("driver", "org.postgresql.Driver") \
        .load()

def get_last_month_data(df):
    current_date = datetime.now()
    last_month = current_date - timedelta(days=30)
    return df.filter(df.played_at >= last_month)