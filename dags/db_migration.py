from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.sql import SQLCheckOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'rahmadiyan',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

proj_dir='/opt/airflow'

tables = ['dim_album', 'dim_song', 'dim_artist', 'fact_history']

with DAG(
    'db_initial_migration',
    default_args=default_args,
    description='DAG to migrate database',
    schedule_interval=None,
    catchup=False,
    concurrency=1,
    max_active_runs=1
) as dag:
    
    start = EmptyOperator(task_id='start')
    
    end = EmptyOperator(task_id='end')
    
    wait_count_check = EmptyOperator(task_id='wait_count_check', trigger_rule='all_success')
    
    wait_migrate_dump = EmptyOperator(task_id='wait_migrate_dump', trigger_rule='all_success')
    
    wait_migrate_load_dim_tables = EmptyOperator(task_id='wait_migrate_load_dim_tables', trigger_rule='all_success')
    
    for table in tables:
        migrate_dump_task = BashOperator(
            task_id=f'source_to_landing_{table}',
            bash_command=f'sh {proj_dir}/bash_scripts/data_dump.sh {table} '
        )
    
        start >> migrate_dump_task >> wait_migrate_dump
    
    for table in tables:
        if table == 'fact_history':
            pass
        else:
            migrate_load_dim_table = BashOperator(
                task_id=f'landing_to_main_{table}',
                bash_command=f'sh {proj_dir}/bash_scripts/data_load.sh {table} '
            )
        
        wait_migrate_dump >> migrate_load_dim_table >> wait_migrate_load_dim_tables
    
    migrate_load_fact = BashOperator(
        task_id='landing_to_main_fact_history',
        bash_command=f'sh {proj_dir}/bash_scripts/data_load.sh fact_history '
    )
    
    wait_migrate_load_dim_tables >> migrate_load_fact
    
    for table in tables:
        count_check = SQLCheckOperator(
            task_id=f'{table}_count_check',
            sql=f'SELECT COUNT(*) FROM {table}',
            conn_id='main_postgres'
        )
        migrate_load_fact >> count_check >> wait_count_check
        
    clean_up_task = BashOperator(
        task_id='clean_up',
        bash_command=f'rm -rf {proj_dir}/data/*'
    )
    
    wait_count_check >> clean_up_task >> end