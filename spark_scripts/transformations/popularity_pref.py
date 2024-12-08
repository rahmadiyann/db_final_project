from pyspark.sql import functions as F
from pyspark.sql.window import Window
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    
from utils.etl_base import SparkETLBase, read_parquet

class PopularityPrefETL(SparkETLBase):
    def transform(self, fact_history_df=None, dim_song_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.fact_history")
        dim_song = dim_song_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_song")

        popularity_pref = fact_history.join(
            dim_song, "song_id"
        ).select(
            ((F.col("popularity") / 10).cast("int")).alias("popularity_bracket")
        ).groupBy("popularity_bracket").agg(
            F.count("*").alias("play_count")
        ).withColumn(
            "popularity_range",
            F.concat(
                (F.col("popularity_bracket") * 10).cast("string"),
                F.lit("-"),
                (F.col("popularity_bracket") * 10 + 10).cast("string")
            )
        ).withColumn(
            "percentage",
            F.round(F.col("play_count") * 100 / F.sum("play_count").over(Window.partitionBy()), 2)
        ).orderBy("popularity_bracket")
        
        popularity_pref.show()
        return popularity_pref