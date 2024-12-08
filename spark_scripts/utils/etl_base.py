from datetime import datetime
import argparse
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from .spark_helper import (
    create_spark_session, 
    load_table, 
    write_parquet, 
    write_table,
    read_parquet
)
import logging
from pyspark.sql.functions import monotonically_increasing_id, row_number

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkETLBase:
    source_tables = [
        "dim_artist",
        "dim_song",
        "dim_album",
        "fact_history"
    ]
    def __init__(self, app_name, stage, destination, table_name, transform_data=False):
        self.spark = create_spark_session(app_name)
        self.stage = stage
        self.destination = destination
        self.table_name = table_name
        self.transform_data = transform_data

    def read_source(self, db=None):
        if self.stage == "source":
            return load_table(self.spark, db, self.table_name)
        elif self.stage == "landing":
            if self.table_name in self.source_tables:
                return read_parquet(self.spark, f"/data/spotify_analysis/landing/{self.table_name}")
            else:
                return None
        elif self.stage == "staging":
            return read_parquet(self.spark, f"/data/spotify_analysis/staging/{self.table_name}")
        else:
            raise ValueError(f"Invalid stage: {self.stage}")

    def write_destination(self, df, db):
        if self.destination == "landing":
            write_parquet(df, self.table_name, "/data/spotify_analysis/landing")
        elif self.destination == "staging":
            write_parquet(df, self.table_name, "/data/spotify_analysis/staging")
        elif self.destination == "datamart":
            write_table(df, db, self.table_name)
        elif self.destination == "hist":
            write_parquet(df, self.table_name, "/data/spotify_analysis/hist")

    def transform(self, df):
        """Override this method in specific ETL classes"""
        return df

    def add_id_column(self, df, id_column_name="id"):
        """Add an auto-incrementing ID column to the DataFrame"""
        window = Window.orderBy(monotonically_increasing_id())
        return df.withColumn(id_column_name, row_number().over(window))

    def run(self):
        try:
            if self.stage == "landing" and self.table_name not in self.source_tables:
                df = self.transform()
            else:
                df = self.read_source(db='source')
                if self.transform_data:
                    df = self.transform(df)
            
            self.write_destination(df, db='datamart')
            
            if self.table_name not in ['public.dim_artist', 'public.dim_song', 'public.dim_album']:
                logger.info(f"=== {self.table_name} Summary ===")
                logger.info(f"Count: {df.count()}\n{df.show(truncate=False)}")
            
        except Exception as e:
            logger.error("An error occurred:", e)
            import traceback
            traceback.print_exc()
            raise e
        finally:
            self.spark.stop()

def get_parser():
    parser = argparse.ArgumentParser(description='Spark ETL Base Script')
    parser.add_argument('--stage', choices=['source', 'landing', 'staging'], required=True,
                      help='Source stage (source, landing, staging)')
    parser.add_argument('--destination', choices=['landing', 'staging', 'datamart', 'hist'], required=True,
                      help='Destination stage (landing, staging, datamart, hist)')
    parser.add_argument('--table', required=True,
                      help='Table name to process')
    parser.add_argument('--transform', action='store_true',
                      help='Whether to apply transformations')
    return parser 