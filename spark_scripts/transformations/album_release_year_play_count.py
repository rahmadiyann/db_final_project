import sys
import os
from pyspark.sql import functions as F
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class AlbumReleaseYearETL(SparkETLBase):
    def transform(self, fact_history_df=None, dim_album_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.fact_history")
        dim_album = dim_album_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_album")

        album_release_year_play_count = fact_history.join(
            dim_album, "album_id"
        ).select(
            F.year("release_date").alias("release_year")
        ).groupBy("release_year").agg(
            F.count("*").alias("play_count")
        ).orderBy(F.desc("release_year")) 
        
        album_release_year_play_count = self.add_id_column(album_release_year_play_count)
        album_release_year_play_count.show()
        return album_release_year_play_count