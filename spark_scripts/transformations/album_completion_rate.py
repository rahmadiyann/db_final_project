import sys
import os
from pyspark.sql import functions as F
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class AlbumCompletionETL(SparkETLBase):
    def transform(self, fact_history_df=None, dim_album_df=None, dim_artist_df=None):
        # Use provided DataFrames or read from landing zone using helper function
        fact_history = fact_history_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.fact_history")
        dim_album = dim_album_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_album")
        dim_artist = dim_artist_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_artist")
        
        album_completion_rate = fact_history.join(
            dim_album, "album_id"
        ).join(
            dim_artist, "artist_id"
        ).groupBy(
            dim_album.title.alias("album_title"), 
            dim_artist.name.alias("artist_name"), 
            "total_tracks"
        ).agg(
            F.countDistinct("song_id").alias("unique_tracks_played")
        ).withColumn(
            "completion_percentage",
            F.round(F.col("unique_tracks_played") * 100 / F.col("total_tracks"), 2)
        ).withColumn(
            "listening_status",
            F.when(F.col("unique_tracks_played") == F.col("total_tracks"), "🌟 Complete")
                .when(F.col("unique_tracks_played") / F.col("total_tracks") >= 0.75, "🎵 Most")
                .when(F.col("unique_tracks_played") / F.col("total_tracks") >= 0.5, "🎧 Half")
                .otherwise("💿 Partial")
        ).filter(
            F.col("total_tracks") > 5
        ).orderBy(
            F.desc("completion_percentage"), F.desc("total_tracks")
        ).limit(10) 
        
        album_completion_rate.show()
        return album_completion_rate