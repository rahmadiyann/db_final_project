from airflow import DAG
from airflow.operators.python import PythonOperator
from helper.send_email import send_email
from airflow.operators.empty import EmptyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
import pendulum

local_tz = pendulum.timezone("Asia/Jakarta")

default_args = {
    'owner': 'rahmadiyan',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 5, tz=local_tz),
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

email_recipient = ['riansshole123@gmail.com', 'riansshole124@gmail.com', 'rahmadiyanmuhammad12@gmail.com', 'rahmadiyan.muhammad1@gmail.com']

def email_operator(task_id, recipient_email, message, subject):
    return PythonOperator(
        task_id=task_id,
        python_callable=send_email,
        op_kwargs={
            'recipient_email': recipient_email,
            'message': message,
            'subject': subject
        }
    )
    
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
    
    wait_email = EmptyOperator(task_id='wait_email', trigger_rule='all_success')
    
    for job in jobs:
        analyze = spark_analysis(job['task_id'], job['script_path'])
        
        start >> analyze >> wait_analysis
        
    for email in email_recipient:
        send_analysis_email = email_operator(
            task_id=f'send_analysis_email_to_{email}',
            recipient_email=email,
            message='This is a test email',
            subject='Test Email'
        )
        
        wait_analysis >> send_analysis_email >> wait_email
    
    wait_email >> end


