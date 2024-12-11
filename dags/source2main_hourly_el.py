from airflow import DAG
from airflow.models.taskinstance import TaskInstance
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime, timedelta
from airflow.models.variable import Variable
from airflow.operators.sql import SQLCheckOperator
from python_scripts.source2main import (
    convert_to_timestamp_ms,
    landing2staging,
    load_dimension_tables,
    load_fact_table,
    to_hist
)
import json
import pendulum
import os

localtz = pendulum.timezone("Asia/Jakarta")
timestamp_ms = Variable.get('last_fetch_time')
tables = ['dim_album', 'dim_song', 'dim_artist', 'fact_history']

default_args = {
    'owner': 'rahmadiyan',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 2, tzinfo=localtz),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

staging_metadata = "{{ task_instance.xcom_pull(task_ids='landing2staging') }}"

def check_last_fetch():
    last_fetch_time = Variable.get('last_fetch_time')
    if last_fetch_time == '0':
        return 'personal2main_full_load'
    return 'source2landing'

def check_for_new_dims(staging_metadata: str):
    staging_metadata = json.loads(staging_metadata)
    staging_path = staging_metadata['staging_file_path']
    
    with open(staging_path, 'r') as f:
        data = json.load(f)
    
    # Check if we have any new dimension data
    if (data['artists_count'] > 0 or 
        data['albums_count'] > 0 or 
        data['songs_count'] > 0):
        return 'enrich_dimensions'
    return 'load_facts'

def cleanup():
    landing_path = f'/data/source2main/landing/*'
    staging_path = f'/data/source2main/staging/*'
    
    # Clean up temporary files
    os.system(f'rm -rf {landing_path}')
    os.system(f'rm -rf {staging_path}')

def check_landing_data(timestamp_ms):
    landing_path = f"/data/source2main/landing/listening_history_{timestamp_ms}.json"
    
    with open(landing_path, 'r') as f:
        data = json.load(f)
    
    if 'error' in data:
        return 'cleanup'
    return 'landing2staging'

def make_load_dim(table, staging_metadata):
    return PythonOperator(
        task_id=f'dim_{table}_insert',
        python_callable=load_dimension_tables,
        op_kwargs={'table': table, 'staging_metadata': staging_metadata}
    )

def update_last_fetch_time():
    timestamp_ms = int(datetime.now().timestamp() * 1000)
    Variable.set('last_fetch_time', timestamp_ms)
    return timestamp_ms

def prepare_soda_check(staging_metadata: str, task_instance: TaskInstance):
    """Prepare Soda check by creating a dynamic check file with the correct timestamp and choose appropriate check"""
    try:
        print(f"Staging metadata: {staging_metadata}")
        # Parse staging metadata if it's a string
        if isinstance(staging_metadata, str):
            staging_metadata = json.loads(staging_metadata)
            
        # Extract values
        played_at_start = staging_metadata['played_at_start']
        played_at_end = staging_metadata['played_at_end']
        fact_count = staging_metadata['listening_history_count']
        dim_song_count = staging_metadata['songs_count']
        dim_album_count = staging_metadata['albums_count']
        dim_artist_count = staging_metadata['artists_count']
        
        # Get task instance runtime and set added_at times
        task_runtime = task_instance.execution_date
        added_at_start_time = task_runtime.replace(minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
        added_at_end_time = task_runtime.replace(minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
        
        # Create environment variables dictionary
        env_vars = {
            "PLAYED_AT_START_TIME": played_at_start,
            "PLAYED_AT_END_TIME": played_at_end,
            "ADDED_AT_START_TIME": added_at_start_time,
            "ADDED_AT_END_TIME": added_at_end_time,
            "FACT_ROW_COUNT": str(fact_count - 1),
            "DIM_SONG_ROW_COUNT": str(dim_song_count - 1),
            "DIM_ALBUM_ROW_COUNT": str(dim_album_count - 1),
            "DIM_ARTIST_ROW_COUNT": str(dim_artist_count - 1)
        }
        
        # Update environment variables
        for key, value in env_vars.items():
            task_instance.xcom_push(key=key, value=value)
        
        # Determine which check to run based on whether dimensions were updated
        if dim_song_count > 0 or dim_album_count > 0 or dim_artist_count > 0:
            return 'dq_test_full'
        return 'dq_test_fact_only'
        
    except Exception as e:
        print(f"Error in prepare_soda_check: {str(e)}")
        print(f"Staging metadata: {staging_metadata}")
        raise e

def create_soda_check_operator(name: str, check_path: str, variables: dict) -> BashOperator:
    """Create a Soda check operator with dynamic variables"""
    variable_str = ' '.join([f'--variable "{k}={v}"' for k, v in variables.items()])
    return BashOperator(
        task_id=f'dq_test_{name}',
        bash_command=f'soda scan -d main_db -c /soda/config/soda_config.yml {check_path} -srf /soda/logs/{name}.log {variable_str}'
    )

def get_soda_variables(task_instance: TaskInstance) -> dict:
    """Get all Soda check variables from XCom"""
    variables = {}
    for key in ['PLAYED_AT_START_TIME', 'PLAYED_AT_END_TIME', 'ADDED_AT_START_TIME',
                'ADDED_AT_END_TIME', 'FACT_ROW_COUNT', 'DIM_SONG_ROW_COUNT',
                'DIM_ALBUM_ROW_COUNT', 'DIM_ARTIST_ROW_COUNT']:
        variables[key] = task_instance.xcom_pull(task_ids='prepare_soda_check', key=key)
    return variables

with DAG(
    'flask_to_main_hourly',
    default_args=default_args,
    description='DAG to fetch recent played songs from Flask API and load to main DB',
    schedule_interval='@hourly',
    concurrency=1,
    max_active_runs=1,
    catchup=False,
    tags=['hourly'],
) as dag:

    start = EmptyOperator(task_id='start')
    
    determine_job = BranchPythonOperator(
        task_id='determine_job',
        python_callable=check_last_fetch
    )
    
    landing_path = f"/data/source2main/landing/listening_history_{timestamp_ms}.json"
    tables = ['dim_artist', 'dim_album', 'dim_song']
            
    source2landing = BashOperator(
        task_id='source2landing',
        bash_command=f"sh /bash_scripts/api_extraction.sh {timestamp_ms} /data/source2main/landing listening_history_{timestamp_ms}.json"
    )
    
    check_landing = BranchPythonOperator(
        task_id='check_landing',
        python_callable=check_landing_data,
        op_kwargs={'timestamp_ms': timestamp_ms}
    )
    
    landing2staging_task = PythonOperator(
        task_id='landing2staging',
        python_callable=landing2staging,
        op_kwargs={
            'file_path': landing_path
        }
    )

    check_dimensions = BranchPythonOperator(
        task_id='check_dimensions',
        python_callable=check_for_new_dims,
        op_kwargs={'staging_metadata': staging_metadata}
    )
    
    update_last_fetch_time_task = PythonOperator(
        task_id='update_flag',
        python_callable=update_last_fetch_time,
        trigger_rule='none_failed_min_one_success'
    )
    
    enrich_dim_artists = make_load_dim('artists', staging_metadata)
    enrich_dim_albums = make_load_dim('albums', staging_metadata)
    enrich_dim_songs = make_load_dim('songs', staging_metadata)
    
    load_facts_task = PythonOperator(
        task_id='load_facts',
        python_callable=load_fact_table,
        op_kwargs={
            'staging_metadata': staging_metadata
        }
    )
    
    enrich_dimensions = EmptyOperator(
        task_id='enrich_dimensions'
    )
    
    hist_task = PythonOperator(
        task_id='staging2hist',
        python_callable=to_hist,
        op_kwargs={
            'staging_metadata': staging_metadata
        },
        trigger_rule='none_failed_min_one_success'
    )
    
    cleanup_task = BashOperator(
        task_id='cleanup',
        bash_command=f'rm -rf /data/source2main/* /sql/migration/*',
        trigger_rule='none_failed_min_one_success'
    )
    
    end = EmptyOperator(
        task_id='end'
    )

    wait_enrich_dimensions = EmptyOperator(
        task_id='wait_enrich_dimensions'
    )
    
    soda_check_prep = BranchPythonOperator(
        task_id='dq_prep',
        python_callable=prepare_soda_check,
        op_kwargs={'staging_metadata': staging_metadata}
    )

    # Create variables dictionary using Jinja templating
    soda_variables = {
        "PLAYED_AT_START_TIME": "{{ task_instance.xcom_pull(task_ids='prepare_soda_check', key='PLAYED_AT_START_TIME') }}",
        "PLAYED_AT_END_TIME": "{{ task_instance.xcom_pull(task_ids='prepare_soda_check', key='PLAYED_AT_END_TIME') }}",
        "ADDED_AT_START_TIME": "{{ task_instance.xcom_pull(task_ids='prepare_soda_check', key='ADDED_AT_START_TIME') }}",
        "ADDED_AT_END_TIME": "{{ task_instance.xcom_pull(task_ids='prepare_soda_check', key='ADDED_AT_END_TIME') }}",
        "FACT_ROW_COUNT": "{{ task_instance.xcom_pull(task_ids='prepare_soda_check', key='FACT_ROW_COUNT') }}",
        "DIM_SONG_ROW_COUNT": "{{ task_instance.xcom_pull(task_ids='prepare_soda_check', key='DIM_SONG_ROW_COUNT') }}",
        "DIM_ALBUM_ROW_COUNT": "{{ task_instance.xcom_pull(task_ids='prepare_soda_check', key='DIM_ALBUM_ROW_COUNT') }}",
        "DIM_ARTIST_ROW_COUNT": "{{ task_instance.xcom_pull(task_ids='prepare_soda_check', key='DIM_ARTIST_ROW_COUNT') }}"
    }

    soda_full_check = create_soda_check_operator(
        'full',
        '/soda/checks/source2main_checks.yml',
        soda_variables
    )

    soda_fact_check = create_soda_check_operator(
        'fact_only',
        '/soda/checks/source2main_fact_checks.yml',
        soda_variables
    )
    
    personal2main_full_load = EmptyOperator(task_id='personal2main_full_load')
    

    # Update task dependencies
    start >> determine_job >> [personal2main_full_load, source2landing]
    
    migrate_dump_fact = BashOperator(
        task_id='dump_fact_history',
        bash_command=f'sh /bash_scripts/data_dump.sh fact_history '
    )
    
    for table in tables:
        migrate_dump_task = BashOperator(
            task_id=f'dump_{table}',
            bash_command=f'sh /bash_scripts/data_dump.sh {table} '
        )
        
        personal2main_full_load >> migrate_dump_task >> migrate_dump_fact
        
    migrate_load_fact = BashOperator(
            task_id='load_fact_history',
            bash_command=f'sh /bash_scripts/data_load.sh fact_history '
        )
    
    for table in tables:
        migrate_load_task = BashOperator(
            task_id=f'load_{table}',
            bash_command=f'sh /bash_scripts/data_load.sh {table} '
        )
        
        migrate_dump_fact >> migrate_load_task >> migrate_load_fact
        
    fact_count_check = SQLCheckOperator(
        task_id='fact_count_check',
        sql=f'SELECT COUNT(*) FROM public.fact_history',
        conn_id='main_postgres'
    )
    
    for table in tables:
        dim_count_check = SQLCheckOperator(
            task_id=f'{table}_count_check',
            sql=f'SELECT COUNT(*) FROM public.{table}',
            conn_id='main_postgres'
        )
        
        migrate_load_fact >> dim_count_check >> fact_count_check
        
    fact_count_check >> update_last_fetch_time_task
        
    source2landing >> check_landing
    
    # Main success path
    check_landing >> landing2staging_task >> check_dimensions
    
    # Path when dimensions need to be enriched
    check_dimensions >> enrich_dimensions
    enrich_dimensions >> [enrich_dim_artists, enrich_dim_albums, enrich_dim_songs] 
    [enrich_dim_artists, enrich_dim_albums, enrich_dim_songs] >> wait_enrich_dimensions 
    wait_enrich_dimensions >> load_facts_task
    
    # Path when no dimension updates needed
    check_dimensions >> load_facts_task
    
    # Branching after load_facts for Soda checks
    load_facts_task >> soda_check_prep >> [soda_full_check, soda_fact_check]
    
    # Common success path
    [soda_full_check, soda_fact_check] >> hist_task >> update_last_fetch_time_task >> cleanup_task
    
    # Error path - only skip to cleanup
    check_landing >> cleanup_task
    
    # Final task
    cleanup_task >> end