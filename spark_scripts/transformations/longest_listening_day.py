import sys
import os
from pyspark.sql import functions as F
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class BiggestListeningDateETL(SparkETLBase):
    def transform(self, fact_history_df=None, dim_album_df=None, dim_artist_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/landing/fact_history")
        
        # Group by date and calculate total milliseconds listened
        listening_by_date = fact_history.groupBy(F.to_date("played_at").alias("date")).agg(
            F.sum("duration_ms").alias("total_milliseconds")
        )
        
        # Order by total_milliseconds descending and limit to 1
        longest_listening_day = listening_by_date.orderBy(F.desc("total_milliseconds")).limit(1)
        
        return longest_listening_day