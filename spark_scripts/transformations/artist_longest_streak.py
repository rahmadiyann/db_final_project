import sys
import os
from pyspark.sql import functions as F
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class ArtistLongestStreak(SparkETLBase):
    def transform(self, fact_history_df=None, dim_artist_df=None, dim_song_df=None, dim_album_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/landing/fact_history")
        dim_artist = dim_artist_df or read_parquet(self.spark, "/data/landing/dim_artist")
        
        # Join fact_history with dim_artist to get artist details
        artist_history = fact_history.join(dim_artist, fact_history.artist_id == dim_artist.artist_id)
        
        # Calculate streaks
        streaks = artist_history.groupBy("artist_id", "name").agg(
            F.countDistinct("played_at").alias("streak_days"),
            F.min("played_at").alias("date_from"),
            F.max("played_at").alias("date_until")
        )
        
        # Order by streak_days descending and limit to 1
        longest_streak = streaks.orderBy(F.desc("streak_days")).limit(1)
        
        return longest_streak