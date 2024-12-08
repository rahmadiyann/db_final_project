import sys
import os
from pyspark.sql import functions as F
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class DayOfWeekETL(SparkETLBase):
    def transform(self, fact_history_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/landing/fact_history")

        daily_stats = fact_history.groupBy(
            F.date_format("played_at", "EEEE").alias("day_of_week")
        ).agg(
            F.count("*").alias("play_count"),
            F.countDistinct("song_id").alias("unique_songs"),
            F.countDistinct("artist_id").alias("unique_artists")
        ).withColumn(
            "song_variety_percentage",
            F.round(F.col("unique_songs") * 100 / F.col("play_count"), 2)
        ).withColumn(
            "artist_variety_percentage",
            F.round(F.col("unique_artists") * 100 / F.col("play_count"), 2)
        ).withColumn(
            "day_number",
            F.when(F.col("day_of_week") == "Sunday", 1)
            .when(F.col("day_of_week") == "Monday", 2)
            .when(F.col("day_of_week") == "Tuesday", 3)
            .when(F.col("day_of_week") == "Wednesday", 4)
            .when(F.col("day_of_week") == "Thursday", 5)
            .when(F.col("day_of_week") == "Friday", 6)
            .when(F.col("day_of_week") == "Saturday", 7)
        ).orderBy("day_number")

        return daily_stats.drop("day_number") 