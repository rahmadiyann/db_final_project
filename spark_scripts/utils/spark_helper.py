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
        'url': f"jdbc:postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_CONTAINER_NAME')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}",
        'host': os.getenv('POSTGRES_CONTAINER_NAME'),
        'port': os.getenv('POSTGRES_PORT'),
        'database': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }
    
def get_analysis_db_properties():
    return {
        'url': f"jdbc:postgresql://{os.getenv('POSTGRES_ANALYSIS_USER')}:{os.getenv('POSTGRES_ANALYSIS_PASSWORD')}@{os.getenv('POSTGRES_ANALYSIS_CONTAINER_NAME')}:{os.getenv('POSTGRES_ANALYSIS_PORT')}/{os.getenv('POSTGRES_ANALYSIS_DB')}",
        'host': os.getenv('POSTGRES_ANALYSIS_CONTAINER_NAME'),
        'port': os.getenv('POSTGRES_ANALYSIS_PORT'),
        'database': os.getenv('POSTGRES_ANALYSIS_DB'),
        'user': os.getenv('POSTGRES_ANALYSIS_USER'),
        'password': os.getenv('POSTGRES_ANALYSIS_PASSWORD')
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