from pyspark.sql import functions as F
from pyspark.sql.window import Window
from spark_scripts.utils.spark_helper import create_spark_session, load_table, get_last_month_data, write_table

query = """
SELECT 
    s.explicit,
    count(*) as play_count,
    round(count(*)::decimal / sum(count(*)) over () * 100, 2) as percentage
FROM fact_history fh
JOIN dim_song s ON fh.song_id = s.song_id
WHERE fh.played_at >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY s.explicit;
"""


def analyze_explicit_content():
    spark = create_spark_session("Explicit Content Analysis")
    
    try:
        # Load tables
        fact_history = load_table(spark, "fact_history")
        dim_song = load_table(spark, "dim_song")
        
        # Get last month's data
        fact_last_month = get_last_month_data(fact_history)
        
        # Analyze explicit content distribution
        explicit_distribution = fact_last_month.join(
            dim_song, "song_id"
        ).groupBy("explicit").agg(
            F.count("*").alias("play_count")
        ).withColumn(
            "percentage",
            F.round(F.col("play_count") * 100 / F.sum("play_count").over(Window.partitionBy()), 2)
        )
        
        # Display results
        print("=== Explicit Content Distribution ===")
        explicit_distribution.show(truncate=False)
        
        write_table(explicit_distribution, "explicit_preference")
        
    finally:
        spark.stop()

if __name__ == "__main__":
    analyze_explicit_content()