from pyspark.sql import functions as F
from pyspark.sql.window import Window
from spark_scripts.utils.spark_helper import create_spark_session, get_main_db_properties, get_analysis_db_properties, load_table, get_last_month_data

query = """
SELECT 
    EXTRACT(HOUR FROM played_at) as hour_of_day,
    count(*) as play_count,
    round(count(*)::decimal / sum(count(*)) over () * 100, 2) as percentage
FROM fact_history
WHERE played_at >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY hour_of_day
ORDER BY percentage DESC;
"""

def analyze_hourly_pattern():
    spark = create_spark_session("Hourly Listening Analysis")
    
    try:
        # Load fact_history table
        fact_history = load_table(spark, "fact_history", get_main_db_properties())
        
        # Get last month's data
        fact_last_month = get_last_month_data(fact_history)
        
        # Analyze hourly distribution
        hour_distribution = fact_last_month.select(
            F.hour("played_at").alias("hour_of_day")
        ).groupBy("hour_of_day").agg(
            F.count("*").alias("play_count")
        ).withColumn(
            "percentage",
            F.round(F.col("play_count") * 100 / F.sum("play_count").over(Window.partitionBy()), 2)
        ).orderBy(F.desc("percentage"))
        
        # Display results
        print("=== Hourly Listening Distribution ===")
        hour_distribution.show(24, False)
        
        hour_distribution.write \
            .mode("overwrite") \
            .jdbc(
                url=get_analysis_db_properties()["url"],
                table="hour_of_day_listening_distribution",
                properties=get_analysis_db_properties()
            )
    finally:
        spark.stop()

if __name__ == "__main__":
    analyze_hourly_pattern()