import sys
import os
from pyspark.sql import functions as F
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class BiggestListeningDateETL(SparkETLBase):
    def transform(self, fact_history_df=None, dim_song_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.fact_history")
        dim_song = dim_song_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_song")
        
        # Join with dim_song to get duration information
        listening_data = fact_history.join(
            dim_song, fact_history.song_id == dim_song.song_id
        )
        
        # Group by date and calculate total milliseconds listened
        listening_by_date = listening_data.groupBy(
            F.to_date("played_at").alias("date")
        ).agg(
            F.sum("duration_ms").alias("total_miliseconds"),
            F.count("*").alias("songs_played")
        )
        
        # Order by total_milliseconds descending and limit to 1
        longest_listening_day = listening_by_date.orderBy(F.desc("total_miliseconds")).limit(1)
        longest_listening_day.show()
        return self.add_id_column(longest_listening_day)