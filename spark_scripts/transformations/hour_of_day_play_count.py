import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    
from utils.etl_base import SparkETLBase, read_parquet
from pyspark.sql import functions as F
from pyspark.sql.window import Window


class HourOfDayPlayCountETL(SparkETLBase):
    def transform(self, fact_history_df=None):
        fact_history = fact_history_df or read_parquet(self.spark, "/data/spotify_analysis/landing/public.fact_history")

        hour_of_day_play_count = fact_history.select(
            F.hour("played_at").alias("hour_of_day")
        ).groupBy("hour_of_day").agg(
            F.count("*").alias("play_count")
        ).withColumn(
            "percentage",
            F.round(F.col("play_count") * 100 / F.sum("play_count").over(Window.partitionBy("hour_of_day")), 2)
        ).orderBy(F.desc("percentage"))
        
        hour_of_day_play_count = self.add_id_column(hour_of_day_play_count)
        hour_of_day_play_count.show()
        return hour_of_day_play_count