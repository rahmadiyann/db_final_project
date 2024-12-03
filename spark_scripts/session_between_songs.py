from pyspark.sql import functions as F
from pyspark.sql.window import Window
from spark_scripts.utils.spark_helper import create_spark_session, load_table, get_last_month_data, write_table

query = """
WITH listening_sessions AS (
    SELECT 
        song_id,
        played_at,
        lead(played_at) OVER (ORDER BY played_at) - played_at as time_to_next_song
    FROM fact_history
    WHERE played_at >= CURRENT_DATE - INTERVAL '1 month'
)
SELECT 
    CASE 
        WHEN extract(epoch from time_to_next_song) < 300 THEN 'Continuous'
        WHEN extract(epoch from time_to_next_song) < 3600 THEN 'Short Break'
        ELSE 'Long Break'
    END as session_type,
    count(*) as count,
    round(count(*)::decimal / sum(count(*)) over () * 100, 2) as percentage
FROM listening_sessions
WHERE time_to_next_song is not null
GROUP BY session_type
ORDER BY 
    CASE session_type 
        WHEN 'Continuous' THEN 1
        WHEN 'Short Break' THEN 2
        ELSE 3
    END;
"""

def analyze_sessions():
    spark = create_spark_session("Listening Session Analysis")
    try:
        fact_history = load_table(spark, "fact_history")
        fact_last_month = get_last_month_data(fact_history)

        window_spec = Window.orderBy("played_at")
        session_analysis = fact_last_month.select(
            "song_id",
            "played_at",
            (F.lead("played_at").over(window_spec) - F.col("played_at")).alias("time_to_next_song")
        ).select(
            F.when(F.unix_timestamp(F.col("time_to_next_song")) < 300, "Continuous")
             .when(F.unix_timestamp(F.col("time_to_next_song")) < 3600, "Short Break")
             .otherwise("Long Break").alias("session_type")
        ).filter(
            F.col("time_to_next_song").isNotNull()
        ).groupBy("session_type").agg(
            F.count("*").alias("count")
        ).withColumn(
            "percentage",
            F.round(F.col("count") * 100 / F.sum("count").over(Window.partitionBy()), 2)
        ).orderBy(
            F.when(F.col("session_type") == "Continuous", 1)
             .when(F.col("session_type") == "Short Break", 2)
             .otherwise(3)
        )

        print("=== Listening Session Analysis ===")
        session_analysis.show(truncate=False)

        write_table(session_analysis, "session_between_songs")
        
    finally:
        spark.stop()

if __name__ == "__main__":
    analyze_sessions()