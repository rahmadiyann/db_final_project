from python_scripts.db_migration import migrate_db
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
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

def get_db_params():
    # Get database parameters from Airflow Variables
    source_db = Variable.get('source_params')
    target_db = Variable.get('target_params')
    
    if not source_db or not target_db:
        raise ValueError("No database parameters found in Airflow Variables")
    
    source_params = {
        'dbname': source_db['database'],
        'user': source_db['user'],
        'password': source_db['password'],
        'host': source_db['host'],
        'port': source_db['port']
    }
    
    target_params = {
        'dbname': target_db['database'],
        'user': target_db['user'],
        'password': target_db['password'],
        'host': target_db['host'],
        'port': target_db['port']
    }
    
    return source_params, target_params

def migrate_db(**context):
    source_params, target_params = get_db_params()
    migrate_db(source_params, target_params)

with DAG(
    'db_initial_migration',
    default_args=default_args,
    description='DAG to migrate database using configurable parameters',
    schedule_interval=None,
    catchup=False
) as dag:
    
    start = EmptyOperator(task_id='start')
    
    end = EmptyOperator(task_id='end')

    migrate_task = PythonOperator(
        task_id='migrate_database',
        python_callable=migrate_db
    )

    start >> migrate_task >> end

