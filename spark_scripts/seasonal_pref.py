from pyspark.sql import functions as F
from spark_scripts.utils.spark_helper import create_spark_session, load_table, get_last_month_data, write_table

query = """
SELECT 
    TO_CHAR(played_at, 'TMMonth') as month,
    count(*) as play_count,
    count(distinct song_id) as unique_songs,
    count(distinct artist_id) as unique_artists,
    round(count(distinct song_id)::decimal / count(*) * 100, 2) as song_variety_percentage,
    round(count(distinct artist_id)::decimal / count(*) * 100, 2) as artist_variety_percentage
FROM fact_history
WHERE played_at >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY month, extract(month from played_at)
ORDER BY extract(month from played_at);
"""

def analyze_seasonal():
    spark = create_spark_session("Seasonal Listening Analysis")
    try:
        fact_history = load_table(spark, "fact_history")
        fact_last_month = get_last_month_data(fact_history)

        monthly_stats = fact_last_month.groupBy(
            F.date_format("played_at", "MMMM").alias("month")
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
        )

        print("=== Monthly Listening Statistics ===")
        monthly_stats.show(truncate=False)

        write_table(monthly_stats, "seasonal_listening_analysis")
        
    finally:
        spark.stop()

if __name__ == "__main__":
    analyze_seasonal()