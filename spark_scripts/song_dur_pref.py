from pyspark.sql import functions as F
from pyspark.sql.window import Window
from spark_scripts.utils.spark_helper import create_spark_session, get_main_db_properties, get_analysis_db_properties, load_table, get_last_month_data

query = """
WITH duration_categories AS (
    SELECT 
        CASE 
            WHEN duration_ms < 180000 THEN 'Short (<3 min)'
            WHEN duration_ms < 300000 THEN 'Medium (3-5 min)'
            ELSE 'Long (>5 min)'
        END as duration_category,
        count(*) as play_count
    FROM fact_history fh
    JOIN dim_song s ON fh.song_id = s.song_id
    WHERE fh.played_at >= CURRENT_DATE - INTERVAL '1 month'
    GROUP BY duration_category
)
SELECT 
    duration_category,
    play_count,
    round(play_count::decimal / sum(play_count) over () * 100, 2) as percentage
FROM duration_categories
ORDER BY play_count DESC;
"""

def analyze_duration():
    spark = create_spark_session("Song Duration Analysis")
    try:
        fact_history = load_table(spark, "fact_history", get_main_db_properties())
        dim_song = load_table(spark, "dim_song", get_main_db_properties())
        fact_last_month = get_last_month_data(fact_history)

        duration_distribution = fact_last_month.join(
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

        print("=== Song Duration Distribution ===")
        duration_distribution.show(truncate=False)
        
        duration_distribution.write \
            .mode("overwrite") \
            .jdbc(
                url=get_analysis_db_properties()["url"],
                table="song_duration_preference",
                properties=get_analysis_db_properties()
            )
    finally:
        spark.stop()

if __name__ == "__main__":
    analyze_duration()