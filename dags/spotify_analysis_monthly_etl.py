from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.common.sql.operators.sql import SQLCheckOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import pendulum
import logging

logger = logging.getLogger(__name__)

local_tz = pendulum.timezone("Asia/Jakarta")

default_args = {
    'owner': 'rahmadiyan',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 4, tzinfo=local_tz),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

doc_md = """
### Spotify Analysis ETL Pipeline

This DAG orchestrates a comprehensive ETL pipeline for analyzing Spotify listening data. The pipeline consists of several stages:

1. **Source to Landing**: 
   - Extracts raw data from source tables (dim_artist, dim_song, dim_album, fact_history)
   - Loads data into landing zone as parquet files

2. **Landing to Staging**:
   - Transforms raw data into analysis tables including:
     - Album completion rates
     - Play counts by release year
     - Listening patterns by day of week
     - Explicit content preferences
     - Hourly listening habits
     - Song popularity preferences
     - Session analysis between songs
     - Duration preferences

3. **Staging to Datamart/Historical**:
   - Loads transformed data into datamart PostgreSQL database
   - Archives data into historical storage
   
4. **Cleanup**:
   - Removes temporary files from landing and staging areas
   - Maintains storage efficiency

The pipeline runs monthly and includes error handling with retries. It uses Apache Spark for large-scale data processing
and ensures data consistency through proper staging and transformation steps.
"""

dag = DAG(
    'spotify_analysis_etl',
    default_args=default_args,
    description='Spotify Analysis ETL Pipeline',
    schedule_interval='@monthly',
    concurrency=2,
    max_active_runs=1,
    catchup=False,
    doc_md=doc_md,
)

def create_spark_task(task_id, stage, destination, table, transform=False):
    args = [
        '--stage', stage,
        '--destination', destination,
        '--table', table
    ]
    if transform:
        args.append('--transform')
        
    return SparkSubmitOperator(
        task_id=f'{task_id}_{table}',
        application='/spark_scripts/run_etl.py',
        name=f'{table} to {destination} ETL',
        conn_id='spark_main',
        application_args=args,
        jars='/jars/postgresql-42.7.4.jar',
        conf={
            "spark.python.files": "/spark_scripts/utils/etl_base.py,/spark_scripts/utils/spark_helper.py",
            "spark.submit.pyFiles": "/spark_scripts/transformations/*.py"
        },
        verbose=True,
        dag=dag,
    )
    
def create_sql_task(task_id, sql, conn_id='analysis_postgres'):
    return SQLCheckOperator(
        task_id=task_id,
        sql=sql,
        conn_id=conn_id,
        dag=dag,
    )
    
def clean_up_data(table: str, source: str):
    logger.info(f'Cleaning up {table} in {source}')
    return BashOperator(
        task_id=f'clean_up_{table}_{source}',
        bash_command=f'rm -rf /data/{source}/* ',
        dag=dag,
    )
    
# Task groups
start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

# Source tables and tasks remain the same
source_tables = [
    'dim_artist',
    'dim_song', 
    'dim_album',
    'fact_history'
]

# Analysis tables remain the same
analysis_tables = [
    'album_completion_rate',
    'album_release_year_play_count',
    'day_of_week',
    'explicit_preference',
    'hour_of_day_play_count',
    'popularity_pref',
    'session_between_songs',
    'song_dur_pref',
]

metrics_table = [
    'top_played_song',
    'longest_listening_day',
    'artist_longest_streak',
    'statistics'
]
 

with TaskGroup("source_to_landing", dag=dag) as source_to_landing_group:
    source_to_landing_tasks = [
        create_spark_task('', 'source', 'landing', table)
        for table in source_tables
    ]

with TaskGroup("landing_to_staging", dag=dag) as landing_to_staging_group:
    with TaskGroup('transformation', dag=dag) as transformation:
        with TaskGroup('transform_analysis', dag=dag) as transformation_analysis:
            landing_to_staging_tasks = [
                create_spark_task('', 'landing', 'staging', f'analysis.{table}', transform=True)
                for table in analysis_tables
            ]
        with TaskGroup('transform_metrics', dag=dag) as transformation_metrics:
            landing_to_staging_tasks = [
                create_spark_task('', 'landing', 'staging', f'metrics.{table}', transform=True)
                for table in metrics_table
            ]
    
    truncate_datamart_task = BashOperator(
        task_id='truncate_datamart',
        bash_command='sh /bash_scripts/truncate_table.sh',
        dag=dag,
    )
    
    for task in transformation:
        task >> truncate_datamart_task

with TaskGroup("staging_to_datamart", dag=dag) as staging_to_datamart_group:
    with TaskGroup("staging_to_datamart_analysis", dag=dag) as staging_to_datamart_analysis_group:
        staging_to_datamart_analysis_tasks = [
            create_spark_task('', 'staging', 'datamart', f"analysis.{table}")
            for table in analysis_tables
        ]
        
    with TaskGroup("staging_to_datamart_metrics", dag=dag) as staging_to_datamart_metrics_group:
        staging_to_datamart_metrics_tasks = [
            create_spark_task('', 'staging', 'datamart', f"metrics.{table}")
            for table in metrics_table
        ]

with TaskGroup("count_check", dag=dag) as count_check_group:
    with TaskGroup("analysis", dag=dag) as count_check_analysis_group:
        count_check_tasks = [
            create_sql_task(f'{table}', f"SELECT COUNT(*) FROM analysis.{table}")
            for table in analysis_tables
        ]
        
    with TaskGroup("metrics", dag=dag) as count_check_metrics_group:
        count_check_tasks = [
            create_sql_task(f'{table}', f"SELECT COUNT(*) FROM metrics.{table}")
            for table in metrics_table
        ]

with TaskGroup("staging2hist", dag=dag) as staging_to_hist_group:
    with TaskGroup("analysis", dag=dag) as staging_to_hist_analysis_group:
        staging_to_hist_tasks = [
            create_spark_task(f'', 'staging', 'hist', f'analysis.{table}')
            for table in analysis_tables
        ]
    with TaskGroup("metrics", dag=dag) as staging_to_hist_metrics_group:
        staging_to_hist_tasks = [
            create_spark_task('', 'staging', 'hist', f'metrics.{table}')
            for table in metrics_table
        ]
with TaskGroup("cleanup", dag=dag) as cleanup_group:
    with TaskGroup('landing_cleanup', dag=dag) as cleanup_landing:
        landing_cleanup_tasks = [clean_up_data(table, 'landing') for table in source_tables]
        
    with TaskGroup('stg_cleanup', dag=dag) as cleanup_stg:
        with TaskGroup('analysis',dag=dag) as cleanup_stg_analysis:
            staging_cleanup_analysis_tasks = [clean_up_data(table, 'staging') for table in analysis_tables]
        with TaskGroup('metrics',dag=dag) as cleanup_stg_metrics:
            staging_cleanup_metrics_tasks = [clean_up_data(table, 'staging') for table in metrics_table]
        
    email_end = EmptyOperator(task_id='email_end', dag=dag)
    
    # Combine all cleanup tasks into a single list
    all_cleanup_tasks = landing_cleanup_tasks + staging_cleanup_analysis_tasks + staging_cleanup_metrics_tasks
    
    for task in all_cleanup_tasks:
        task >> email_end

# Set up dependencies
start >> source_to_landing_group >> landing_to_staging_group >> staging_to_datamart_group >> count_check_group >> staging_to_hist_group >> cleanup_group >> end