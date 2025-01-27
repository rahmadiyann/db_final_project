import sys
import os
from pyspark.sql import functions as F
from pyspark.sql.window import Window
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    
from utils.etl_base import SparkETLBase, read_parquet

class ExplicitPreferenceETL(SparkETLBase):
    def transform(self, fact_history_df=None, dim_song_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.fact_history")
        dim_song = dim_song_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_song")
        
        total_play_count = fact_history.count()

        explicit_preference = fact_history.join(
            dim_song, "song_id"
        ).groupBy("explicit").agg(
            F.count("*").alias("play_count")
        ).withColumn(
            "percentage",
            F.round(F.col("play_count") * 100 / total_play_count, 2)
        ) 
        
        explicit_preference = self.add_id_column(explicit_preference)
        explicit_preference.show()
        return explicit_preference