from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.common.sql.operators.sql import SQLCheckOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
import pendulum
import logging
from sensors.sql_data_sensor import LastMonthDataSensor
from python_scripts.email_util import sendEmail

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
    description='Spotify Analysis monthly ETL Pipeline',
    schedule_interval='@monthly',
    concurrency=4,
    max_active_runs=1,
    catchup=False,
    doc_md=doc_md,
    tags=['monthly'],
)

email_receiver = ['rahmadiyanmuhammad12@gmail.com']

def create_spark_task(task_id, stage, destination, table, transform=False):
    application_name = f"{table}_{stage}2{destination}"
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
        name=application_name,
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
    
def create_sql_task(task_id, sql, conn_id='main_postgres'):
    return SQLCheckOperator(
        task_id=task_id,
        sql=sql,
        conn_id=conn_id,
        dag=dag,
    )
    
def create_soda_check_task(task_id, table):
    schema = table.split('.')[0]
    table_name = table.split('.')[1]
    
    db = "analysis_db" if schema == "analysis" else "metrics_db"
    
    return BashOperator(
        task_id=task_id,
        bash_command=f'soda scan -d {db} -c /soda/config/soda_config_{schema}.yml /soda/checks/spotify_etl/{schema}/{schema}.{table_name}.yml -srf /soda/logs/{task_id}.log',
        dag=dag,
    )
    
def clean_up_data(source: str):
    logger.info(f'Cleaning up {source}')
    return BashOperator(
        task_id=f'clean_up_{source}',
        bash_command=f'rm -rf /data/spotify_analysis/{source}/* ',
        dag=dag,
    )
    
# =========== SET EMAIL START/END NOTIFICATION ===========
def email_start(**context):
    buss_date = context['ds']
    message = f"""
            subject : ETL {dag.dag_id} is Started.<br/><br/>
            Message :
                Dear All, <br/><br/>

                Monthly ETL {dag.dag_id} for Business Date {buss_date} is Started.
    """
    sendEmail(email_string=message, subject="ETL {0} is Started.".format(dag.dag_id))

def email_end(**context):
    buss_date = context['ds']
    message = f"""
        subject : ETL {dag.dag_id} is Finished.<br/><br/>
        Message :
            Dear All, <br/><br/>

            Monthly ETL {dag.dag_id} for Business Date {buss_date} is Finished.
    """
    sendEmail(email_string=message, subject="ETL {0} is Finished.".format(dag.dag_id))
    
# Task groups
start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

# Add the sensor as the first task
check_last_month_data = LastMonthDataSensor(
    task_id='data_sensor',
    poke_interval=150,  # Check every 5 minutes
    timeout=60 * 60 * 2,  # Timeout after 2 hours
    mode='reschedule',
    soft_fail=False,  # Fail the DAG if data is not found
)

# Source tables and tasks remain the same
source_tables = [
    'dim_artist',
    'dim_song', 
    'dim_album',
    'fact_history'
]

# Analysis tables remain the same
analysis_tables = [
    'album_completion_analysis',
    'album_release_year_play_count',
    'day_of_week_listening_distribution',
    'explicit_preference',
    'hour_of_day_listening_distribution',
    'song_popularity_distribution',
    'session_between_songs',
    'song_duration_preference',
]

metrics_table = [
    'top_played_song',
    'longest_listening_day',
    'artist_longest_streak',
    'statistics'
]
 

with TaskGroup("source_to_landing", dag=dag) as source_to_landing_group:
    source_to_landing_tasks = [
        create_spark_task('', 'source', 'landing', f'public.{table}')
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
        bash_command='sh /bash_scripts/truncate_table.sh ',
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

with TaskGroup("checks", dag=dag) as checks_group:
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
    
    with TaskGroup("soda_check", dag=dag) as soda_check_group:
        with TaskGroup("analysis", dag=dag) as soda_check_analysis_group:
            soda_check_tasks = [
                create_soda_check_task(f'soda_check_{table}', f"analysis.{table}")
                for table in analysis_tables
            ]
        
        with TaskGroup("metrics", dag=dag) as soda_check_metrics_group:
            soda_check_tasks = [
                create_soda_check_task(f'soda_check_{table}', f"metrics.{table}")
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
    cleanup_tasks = [clean_up_data(source) for source in ['landing', 'staging']]
        
        
op_email_start = PythonOperator(
    task_id='email_start',
    python_callable=email_start,
    provide_context=True,
    dag=dag
)

op_email_end = PythonOperator(
    task_id='email_end',
    python_callable=email_end,
    provide_context=True,
    dag=dag
)


# Set up dependencies
start >> check_last_month_data >> op_email_start  >> source_to_landing_group >> landing_to_staging_group >> staging_to_datamart_group >> checks_group >> staging_to_hist_group >> cleanup_group >> op_email_end >> end
