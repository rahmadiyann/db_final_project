from pyspark.sql import functions as F
from spark_scripts.utils.spark_helper import create_spark_session, load_table, get_last_month_data, write_table

query = """
WITH album_stats AS (
    SELECT 
        a.album_id,
        a.title as album_title,
        ar.name as artist_name,
        a.total_tracks,
        count(distinct fh.song_id) as unique_tracks_played
    FROM fact_history fh
    JOIN dim_album a ON fh.album_id = a.album_id
    JOIN dim_artist ar ON fh.artist_id = ar.artist_id
    WHERE fh.played_at >= CURRENT_DATE - INTERVAL '1 month'
    GROUP BY a.album_id, a.title, ar.name, a.total_tracks
)
SELECT 
    album_title,
    artist_name,
    total_tracks,
    unique_tracks_played,
    round(unique_tracks_played::decimal / total_tracks * 100, 2) as completion_percentage,
    CASE 
        WHEN unique_tracks_played = total_tracks THEN '🌟 Complete'
        WHEN unique_tracks_played::decimal / total_tracks >= 0.75 THEN '🎵 Most'
        WHEN unique_tracks_played::decimal / total_tracks >= 0.5 THEN '🎧 Half'
        ELSE '💿 Partial'
    END as listening_status
FROM album_stats
WHERE total_tracks > 5
ORDER BY completion_percentage DESC, total_tracks DESC
LIMIT 10;
"""

def analyze_album_completion():
    spark = create_spark_session("Album Completion Analysis")
    try:
        fact_history = load_table(spark, "fact_history")
        dim_album = load_table(spark, "dim_album")
        dim_artist = load_table(spark, "dim_artist")
        fact_last_month = get_last_month_data(fact_history)

        album_completion = fact_last_month.join(
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

        print("=== Album Completion Analysis ===")
        album_completion.show(truncate=False)
        # Save results to the analysis database
        write_table(album_completion, "album_completion_analysis")
    finally:
        spark.stop()

if __name__ == "__main__":
    analyze_album_completion()