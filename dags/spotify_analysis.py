from airflow import DAG
from airflow.operators.python import PythonOperator
from helper.send_email import sendEmail
from airflow.operators.empty import EmptyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
import pendulum

local_tz = pendulum.timezone("Asia/Jakarta")

default_args = {
    'owner': 'rahmadiyan',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 2, tzinfo=local_tz),
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

jobs = [
    {
        'task_id': 'song_duration_preference',
        'script_path': '/spark-scripts/song_dur_pref.py'
    },
    {
        'task_id': 'popularity_preference',
        'script_path': '/spark-scripts/popularity_pref.py'
    },
    {
        'task_id': 'album_completion_rate',
        'script_path': '/spark-scripts/album_completion_rate.py'
    },
    {
        'task_id': 'album_release_year_play_count',
        'script_path': '/spark-scripts/album_release_year_play_count.py'
    },
    {
        'task_id': 'explicit_content_preference',
        'script_path': '/spark-scripts/explicit_pref.py'
    },
    {
        'task_id': 'hour_of_day_play_count',
        'script_path': '/spark-scripts/hour_of_day_play_count.py'
    },
    {
        'task_id': 'seasonal_preference',
        'script_path': '/spark-scripts/seasonal_pref.py'
    },
    {
        'task_id': 'session_between_songs',
        'script_path': '/spark-scripts/session_between_songs.py'
    }
]
    
def spark_analysis(task_id: str, script_path: str) -> SparkSubmitOperator:
    return SparkSubmitOperator(
        task_id=task_id,
        application=script_path,
        conn_id='spark_main',
        jars='/opt/airflow/jars/pg_jdbc.jar',
        dag=dag
    )
    
with DAG(
    'music_listening_analysis',
    default_args=default_args,
    description='Music listening analysis report',
    schedule_interval='@monthly',
    catchup=False
) as dag:
    
    start = EmptyOperator(task_id='start')
    
    end = EmptyOperator(task_id='end', trigger_rule='all_done')
    
    wait_analysis = EmptyOperator(task_id='wait_analysis', trigger_rule='all_success')
    
    send_email = PythonOperator(
        task_id='send_email',
        python_callable=sendEmail,
        op_kwargs={
            'message': 'This is a test email',
            'subject': 'Test Email'
        },
        dag=dag
    )
    
    for job in jobs:
        analyze = spark_analysis(job['task_id'], job['script_path'])
        
        start >> analyze >> wait_analysis
        

    
    wait_analysis >> send_email >> end


