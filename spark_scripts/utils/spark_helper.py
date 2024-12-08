# spark_utils.py
from pyspark.sql import SparkSession, DataFrame
from datetime import datetime, timedelta
import os

def create_spark_session(app_name):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars", "/jars/postgresql-42.7.4.jar ") \
        .getOrCreate()

def get_db_properties(db: str = "source", table: str = None):
    """Get database connection properties based on database type and table name.
    
    Args:
        db: Database type ("source" or "datamart")
        table: Table name including schema (e.g. "public.dim_artist")
        
    Returns:
        dict: Database connection properties
    """
    if not table:
        raise ValueError("Table name is required")
    
    # Common properties for both source and datamart
    props = {
        'url': os.getenv('DATAENG_JDBC_POSTGRES_URI'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'driver': 'org.postgresql.Driver',
        'dbtable': table
    }
    
    if db not in ["source", "datamart"]:
        raise ValueError(f"Invalid database: {db}")
        
    return props

def load_table(spark, db, table_name):
    props = get_db_properties(db, table_name)
    
    df = spark.read \
        .format("jdbc") \
        .option("url", props['url']) \
        .option("dbtable", props['table']) \
        .option("user", props['user']) \
        .option("password", props['password']) \
        .option("driver", props['driver']) \
        .load()
        
    if table_name == 'public.fact_history':
        last_month_history = get_last_month_data(df)
        return last_month_history
    
    return df
    
    
def write_csv(df: DataFrame, table_name: str, path: str):
    month_year = datetime.now().strftime("%Y%m")
    os.makedirs(f"{path}/{table_name}", exist_ok=True)
    df.write.mode("overwrite").csv(f"{path}/{table_name}/{table_name}_{month_year}.csv")

def read_csv(spark: SparkSession, path: str):
    return spark.read.csv(path, header=True, inferSchema=True)

def write_table(df: DataFrame, db: str, table_name: str):
    try:
        df.write \
            .mode("overwrite") \
            .format("jdbc") \
            .options(**get_db_properties(db, table_name)) \
            .save()
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        
def get_last_month_data(df):
    current_date = datetime.now()
    # Get the first day of the current month
    start_of_current_month = current_date.replace(day=1, hour=0, minute=0, second=0)
    # Get the first day of the last month
    start_of_last_month = (start_of_current_month - timedelta(days=1)).replace(day=1)
    
    # Filter the DataFrame for records from the last month
    return df.filter((df.played_at >= start_of_last_month) & (df.played_at < start_of_current_month))

def write_parquet(df: DataFrame, table_name: str, path: str):
    """Write parquet file to a specific path with consistent structure.
    
    Args:
        df: DataFrame to write
        table_name: Name of the table
        path: Base path (/data/landing, /data/staging, etc.)
    """
    month_year = datetime.now().strftime("%Y%m")
    path = path.rstrip('/')
    os.makedirs(f"{path}/{table_name}", exist_ok=True)
    df.write.mode("overwrite").parquet(f"{path}/{table_name}/{table_name}_{month_year}.parquet")

def read_parquet(spark: SparkSession, path: str):
    """Read parquet file from a specific path with consistent structure.
    
    Args:
        spark: SparkSession
        path: Full path including table name (/data/spotify_analysis/landing/dim_song, etc.)
    """
    month_year = datetime.now().strftime("%Y%m")
    path = path.rstrip('/')
    table_name = path.split('/')[-1]
    base_path = '/'.join(path.split('/')[:-1])
    full_path = f"{base_path}/{table_name}/{table_name}_{month_year}.parquet"
    return spark.read.parquet(full_path)