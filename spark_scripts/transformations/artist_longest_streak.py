import sys
import os
from pyspark.sql import functions as F
from pyspark.sql.window import Window
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class ArtistLongestStreak(SparkETLBase):
    def transform(self, fact_history_df=None, dim_artist_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.fact_history")
        dim_artist = dim_artist_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_artist")
        
        # Join and get distinct dates per artist
        artist_daily = fact_history.join(
            dim_artist, fact_history.artist_id == dim_artist.artist_id
        ).select(
            dim_artist.artist_id,
            dim_artist.name.alias("artist_name"),
            dim_artist.image_url.alias("artist_image_url"),
            F.to_date(fact_history.played_at).alias("play_date")
        ).distinct()
        
        # Window for detecting breaks in consecutive dates
        window = Window.partitionBy("artist_id", "play_date").orderBy("play_date")
        
        # Calculate date difference with previous date
        consecutive_days = artist_daily.withColumn(
            "date_diff", 
            F.datediff(
                F.col("play_date"), 
                F.lag("play_date", 1).over(window)
            )
        )
        
        # Assign group number when streak breaks (date_diff > 1)
        streak_groups = consecutive_days.withColumn(
            "streak_group",
            F.sum(
                F.when(F.col("date_diff") > 1, 1)
                .when(F.col("date_diff").isNull(), 1)
                .otherwise(0)
            ).over(window)
        )
        
        # Calculate streak lengths
        streaks = streak_groups.groupBy(
            "artist_id",
            "artist_name",
            "artist_image_url",
            "streak_group"
        ).agg(
            F.count("*").alias("streak_days"),
            F.min("play_date").alias("date_from"),
            F.max("play_date").alias("date_until")
        )
        
        # Get the longest streak and drop streak_group column
        longest_streak = streaks.orderBy(F.desc("streak_days")).limit(1).drop("streak_group")
        
        longest_streak = self.add_id_column(longest_streak)
        return longest_streak