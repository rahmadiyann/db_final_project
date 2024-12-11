from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta
from python_scripts.main2genai import source2landing, generate_content, ingest_email_content, sendEmail
from python_scripts.models import (
    ArtistLongestStreak, AlbumCompletionAnalysis, AlbumReleaseYearPlayCount,
    LongestListeningDay, DayOfWeekListeningDistribution, HourOfDayListeningDistribution,
    Statistics, TopPlayedSong, SessionBetweenSongs, SongDurationPreference,
    SongPopularityDistribution, ExplicitPreference
)
import pendulum

local_tz = pendulum.timezone("Asia/Jakarta")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'monthly_wrapped_email_blast',
    default_args=default_args,
    description='Monthly Spotify Wrapped Email Blast',
    schedule_interval='@monthly',  # Run at midnight on the first day of every month
    start_date=datetime(2024, 12, 9, tzinfo=local_tz),
    catchup=False,
    concurrency=1,
    max_active_runs=1,
    tags=['monthly'],
) as dag:
    
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end', trigger_rule='all_success')

    datamart_sensor = ExternalTaskSensor(
        task_id='datamart_sensing',
        external_dag_id='spotify_analysis_etl',
        external_task_id='end',
        mode='reschedule',
        poke_interval=60,
        timeout=60 * 60 * 24,
        dag=dag,
    )

    # Task to extract data and save to JSON
    extract_data = PythonOperator(
        task_id='source_to_landing',
        python_callable=source2landing,
        op_kwargs={
            'ArtistLongestStreak': ArtistLongestStreak,
            'AlbumCompletionAnalysis': AlbumCompletionAnalysis,
            'AlbumReleaseYearPlayCount': AlbumReleaseYearPlayCount,
            'LongestListeningDay': LongestListeningDay,
            'DayOfWeekListeningDistribution': DayOfWeekListeningDistribution,
            'HourOfDayListeningDistribution': HourOfDayListeningDistribution,
            'Statistics': Statistics,
            'TopPlayedSong': TopPlayedSong,
            'SessionBetweenSongs': SessionBetweenSongs,
            'SongDurationPreference': SongDurationPreference,
            'SongPopularityDistribution': SongPopularityDistribution,
            'ExplicitPreference': ExplicitPreference
        }
    )
    
    clean_up_data = BashOperator(
        task_id='clean_up_data',
        bash_command='rm -rf /data/spotify_analysis/monthly_email_blast/landing/* && rm -rf /data/spotify_analysis/monthly_email_blast/staging/*',
        dag=dag,
    )
    
    to_hist = BashOperator(
        task_id='to_hist',
        bash_command='mkdir -p /data/monthly_email_blast/hist/ && mv /data/monthly_email_blast/staging/* /data/monthly_email_blast/hist/',
        dag=dag,
    )

    # Task to generate AI content
    generate_ai_content = PythonOperator(
        task_id='generate_ai_content',
        python_callable=generate_content,
        op_kwargs={
            'data_file': "{{ task_instance.xcom_pull(task_ids='source_to_landing') }}"
        }
    )

    # Task to create email HTML
    create_email = PythonOperator(
        task_id='create_email_content',
        python_callable=ingest_email_content,
        op_kwargs={
            'data_file': "{{ task_instance.xcom_pull(task_ids='source_to_landing') }}",
            'content_file': "{{ task_instance.xcom_pull(task_ids='generate_ai_content') }}"
        }
    )

    # Task to send email
    send_email = PythonOperator(
        task_id='send_email',
        python_callable=sendEmail,
        op_kwargs={
            'email_file': "{{ task_instance.xcom_pull(task_ids='create_email_content') }}"
        }
    )

    # Set up dependencies
    start >> datamart_sensor >> extract_data >> generate_ai_content >> create_email >> send_email >> to_hist >> clean_up_data >> end