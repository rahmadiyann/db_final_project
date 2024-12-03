# spark_utils.py
from pyspark.sql import SparkSession, DataFrame
from datetime import datetime, timedelta
import os

def create_spark_session(app_name):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars", "/opt/jars/postgresql-42.7.4.jar") \
        .getOrCreate()

def get_main_db_properties(table: str = None):
    if not table:
        raise ValueError("Table name is required")
    
    return {
        'url': f"jdbc:postgresql://{os.getenv('POSTGRES_CONTAINER_NAME')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}",
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'driver': 'org.postgresql.Driver',
        'table': table
    }
    
def get_analysis_db_properties(table: str = None):
    if not table:
        raise ValueError("Table name is required")
    
    return {
        'url': f"jdbc:postgresql://{os.getenv('POSTGRES_ANALYSIS_CONTAINER_NAME')}:{os.getenv('POSTGRES_ANALYSIS_PORT')}/{os.getenv('POSTGRES_ANALYSIS_DB')}",
        'user': os.getenv('POSTGRES_ANALYSIS_USER'),
        'password': os.getenv('POSTGRES_ANALYSIS_PASSWORD'),
        'driver': 'org.postgresql.Driver',
        'dbtable': table
    }

def load_table(spark, table_name):
    props = get_main_db_properties(table_name)
    
    return spark.read \
        .format("jdbc") \
        .option("url", props['url']) \
        .option("dbtable", props['table']) \
        .option("user", props['user']) \
        .option("password", props['password']) \
        .option("driver", props['driver']) \
        .load()

def write_table(df: DataFrame, table_name: str):
    try:
        df.write \
            .mode("overwrite") \
            .format("jdbc") \
            .options(**get_analysis_db_properties(table_name)) \
            .save()
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        
def get_last_month_data(df):
    current_date = datetime.now()
    last_month = current_date - timedelta(days=30)
    return df.filter(df.played_at >= last_month)