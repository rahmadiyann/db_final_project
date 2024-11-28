from pyspark.sql import functions as F
from pyspark.sql.window import Window
from spark_scripts.utils.spark_helper import create_spark_session, get_main_db_properties, get_analysis_db_properties, load_table, get_last_month_data

query = """
WITH popularity_brackets AS (
    SELECT 
        width_bucket(s.popularity, 0, 100, 10) as popularity_bracket,
        count(*) as play_count
    FROM fact_history fh
    JOIN dim_song s ON fh.song_id = s.song_id
    WHERE fh.played_at >= CURRENT_DATE - INTERVAL '1 month'
    GROUP BY popularity_bracket
)
SELECT 
    ((popularity_bracket - 1) * 10) || '-' || (popularity_bracket * 10) as popularity_range,
    play_count,
    round(play_count::decimal / sum(play_count) over () * 100, 2) as percentage
FROM popularity_brackets
ORDER BY popularity_bracket;
"""

def analyze_popularity():
    spark = create_spark_session("Song Popularity Analysis")
    try:
        fact_history = load_table(spark, "fact_history", get_main_db_properties())
        dim_song = load_table(spark, "dim_song", get_main_db_properties())
        fact_last_month = get_last_month_data(fact_history)

        popularity_distribution = fact_last_month.join(
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

        print("=== Song Popularity Distribution ===")
        popularity_distribution.show(truncate=False)
        
        popularity_distribution.write \
            .mode("overwrite") \
            .jdbc(
                url=get_analysis_db_properties()["url"],
                table="song_popularity_distribution",
                properties=get_analysis_db_properties()
            )
    finally:
        spark.stop()

if __name__ == "__main__":
    analyze_popularity()