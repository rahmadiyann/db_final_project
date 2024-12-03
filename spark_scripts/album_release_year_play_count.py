from pyspark.sql import functions as F
from spark_scripts.utils.spark_helper import create_spark_session, load_table, get_last_month_data, write_table

query = """
SELECT
    EXTRACT(YEAR FROM a.release_date) AS release_year,
    count(*) as play_count
FROM fact_history fh
JOIN dim_album a ON fh.album_id = a.album_id
WHERE fh.played_at >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY release_year
ORDER BY release_year DESC;
"""

def analyze_release_years():
    spark = create_spark_session("Release Year Analysis")
    
    try:
        # Load tables
        fact_history = load_table(spark, "fact_history")
        dim_album = load_table(spark, "dim_album")
        
        # Get last month's data
        fact_last_month = get_last_month_data(fact_history)
        
        # Analyze release year distribution
        year_distribution = fact_last_month.join(
            dim_album, "album_id"
        ).select(
            F.year("release_date").alias("release_year")
        ).groupBy("release_year").agg(
            F.count("*").alias("play_count")
        ).orderBy(F.desc("release_year"))
        
        # Display results
        print("=== Release Year Distribution ===")
        year_distribution.show(truncate=False)
        
        write_table(year_distribution, "album_release_year_play_count")
        
    finally:
        spark.stop()

if __name__ == "__main__":
    analyze_release_years()