import sys
import os
from pyspark.sql import functions as F
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class StatisticsETL(SparkETLBase):
    def transform(self, fact_history_df=None, dim_song_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.fact_history")
        dim_song = dim_song_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_song")
        
        # Join fact_history with dim_song to get duration information
        listening_data = fact_history.join(dim_song, "song_id")
        
        # Calculate total miliseconds listened
        total_miliseconds = listening_data.agg(
            F.sum("duration_ms").alias("total_miliseconds")
        )
        
        # Calculate total songs played
        total_songs_played = fact_history.agg(
            F.countDistinct("song_id").alias("total_songs_played")
        )
        
        # Combine both metrics into a single DataFrame
        statistics = total_miliseconds.crossJoin(total_songs_played)
        
        statistics.show()
        statistics = self.add_id_column(statistics)
        return statistics