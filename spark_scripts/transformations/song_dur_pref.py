import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    
from utils.etl_base import SparkETLBase, read_parquet
from pyspark.sql import functions as F
from pyspark.sql.window import Window

class SongDurPrefETL(SparkETLBase):
    def transform(self, fact_history_df=None, dim_song_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/landing/fact_history")
        dim_song = dim_song_df or read_parquet(self.spark, "/data/landing/dim_song")

        return fact_history.join(
            dim_song, "song_id"
        ).select(
            F.when(F.col("duration_ms") < 180000, "Short (<3 min)")
                .when(F.col("duration_ms") < 300000, "Medium (3-5 min)")
                .otherwise("Long (>5 min)").alias("duration_category")
        ).groupBy("duration_category").agg(
            F.count("*").alias("play_count")
        ).withColumn(
            "percentage",
            F.round(F.col("play_count") * 100 / F.sum("play_count").over(Window.partitionBy()), 2)
        ).orderBy(F.desc("play_count"))