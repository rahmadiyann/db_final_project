import sys
import os
from pyspark.sql import functions as F
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.etl_base import SparkETLBase, read_parquet

class TopSongDetail(SparkETLBase):
    def transform(self, fact_history_df=None, dim_artist_df=None, dim_song_df=None, dim_album_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.fact_history")
        dim_song = dim_song_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_song")
        dim_artist = dim_artist_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.dim_artist")
        
        # Join fact_history with dim_song and dim_artist to get song and artist details
        song_details = fact_history.join(
            dim_song, fact_history.song_id == dim_song.song_id
        ).join(
            dim_artist, fact_history.artist_id == dim_artist.artist_id
        ).select(
            dim_song.song_id.alias("song_id"),
            dim_song.title.alias("song_title"),
            dim_artist.artist_id.alias("artist_id"),
            dim_artist.name.alias("artist_name"),
            dim_artist.image_url.alias("artist_image_url"),
            fact_history.played_at
        )
        
        # Group by song and artist to get play count and date ranges
        top_played_songs = song_details.groupBy(
            "song_id", 
            "song_title", 
            "artist_id", 
            "artist_name",
            "artist_image_url"
        ).agg(
            F.count("*").alias("play_count"),
            F.min("played_at").alias("first_played_at"),
            F.max("played_at").alias("last_played_at")
        )
        
        # Order by play_count descending and limit to 1
        top_song = top_played_songs.orderBy(F.desc("play_count")).limit(1)
        
        top_song = self.add_id_column(top_song)
        top_song.show()
        return top_song