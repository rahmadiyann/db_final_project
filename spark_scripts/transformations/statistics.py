import sys
import os
from pyspark.sql import functions as F
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class StatisticsETL(SparkETLBase):
    def transform(self, fact_history_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/landing/fact_history")
        
        # Calculate total miliseconds listened
        total_miliseconds = fact_history.agg(
            F.sum("duration_ms").alias("total_miliseconds")
        )
        
        # Calculate total songs played
        total_songs_played = fact_history.agg(
            F.countDistinct("song_id").alias("total_songs_played")
        )
        
        # Combine both metrics into a single DataFrame
        statistics = total_miliseconds.crossJoin(total_songs_played)
        
        return statistics