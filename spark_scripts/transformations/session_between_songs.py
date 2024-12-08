import os
import sys

# Add the spark_scripts directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.etl_base import SparkETLBase, read_parquet
from pyspark.sql import functions as F
from pyspark.sql.window import Window

class SessionBetweenSongsETL(SparkETLBase):
    def transform(self, fact_history_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/landing/fact_history")

        # Calculate the time to the next song
        window_spec = Window.orderBy("played_at")
        listening_sessions_df = fact_history.withColumn(
            "time_to_next_song",
            (F.unix_timestamp(F.lead("played_at").over(window_spec)) - F.unix_timestamp("played_at"))
        )

        # Define session types based on time_to_next_song
        session_type_df = listening_sessions_df.withColumn(
            "session_type",
            F.when(F.col("time_to_next_song") < 300, "Continuous")
            .when(F.col("time_to_next_song") < 3600, "Short Break")
            .otherwise("Long Break")
        )

        # Group by session type and calculate counts
        session_counts_df = session_type_df.groupBy("session_type").agg(
            F.count("*").alias("count")
        )

        # Calculate total count for percentage calculation
        total_count = session_counts_df.agg(F.sum("count").alias("total_count")).collect()[0]["total_count"]

        # Calculate percentages
        return session_counts_df.withColumn(
            "percentage",
            F.round((F.col("count") / total_count) * 100, 2)
        ).orderBy(
            F.when(F.col("session_type") == "Continuous", 1)
            .when(F.col("session_type") == "Short Break", 2)
            .otherwise(3)
        )