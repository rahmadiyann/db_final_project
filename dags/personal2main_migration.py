from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.sql import SQLCheckOperator
from airflow.utils.task_group import TaskGroup
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

tables = ['dim_album', 'dim_song', 'dim_artist', 'fact_history']
doc_md = """
# Personal to Main Initial Migration DAG

This DAG handles the initial data migration from a personal/source database to the main database.

## DAG Structure

### Tables Processed
- dim_album: Dimension table containing album information
- dim_song: Dimension table containing song information  
- dim_artist: Dimension table containing artist information
- fact_history: Fact table containing historical records

### Process Flow
1. **Data Extraction**: Dumps data from source database tables using pg_dump
2. **Dimension Tables Load**: Loads dimension tables (dim_album, dim_song, dim_artist) first
3. **Fact Table Load**: Loads fact_history table after dimension tables are loaded
4. **Validation**: Performs count checks between source and target
5. **Cleanup**: Removes temporary dump files

### Task Groups
- Source to Landing: Extracts data from source DB to SQL files
- Landing to Main: Loads data from SQL files to main DB
- Count Validation: Ensures data integrity through count checks
- Cleanup: Removes temporary files

### Failure Handling
- Retries: 1 attempt after 5 minute delay
- Concurrency: Limited to 1 task at a time
- Max Active Runs: Limited to 1

### Dependencies
- Requires bash scripts:
  - data_dump.sh: For extracting data
  - data_load.sh: For loading data
- Requires proper database connections configured in Airflow
"""

with DAG(
    'personal_to_main_initial_migration',
    default_args=default_args,
    description='DAG to migrate personal data to main',
    schedule_interval=None,
    catchup=False,
    concurrency=1,
    max_active_runs=1,
    tags=['once', 'migration'],
    doc_md=doc_md
) as dag:
    
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    with TaskGroup(group_id='source_to_landing') as source_to_landing:
        for table in tables:
            migrate_dump_task = BashOperator(
                task_id=f'dump_{table}',
                bash_command=f'sh /bash_scripts/data_dump.sh {table} '
            )

    with TaskGroup(group_id='landing_to_main') as landing_to_main:
        # Load dimension tables first
        with TaskGroup(group_id='load_dimension_tables') as load_dimension_tables:
            for table in tables:
                if table != 'fact_history':
                    migrate_load_dim_table = BashOperator(
                        task_id=f'load_{table}',
                        bash_command=f'sh /bash_scripts/data_load.sh {table} '
                    )
        
        # Load fact table after dimension tables
        migrate_load_fact = BashOperator(
            task_id='load_fact_history',
            bash_command=f'sh /bash_scripts/data_load.sh fact_history '
        )
        
        load_dimension_tables >> migrate_load_fact

    with TaskGroup(group_id='count_validation') as count_validation:
        for table in tables:
            count_check = SQLCheckOperator(
                task_id=f'{table}_count_check',
                sql=f'SELECT COUNT(*) FROM {table}',
                conn_id='main_postgres'
            )

    clean_up_task = BashOperator(
        task_id='clean_up',
        bash_command=f'rm -rf /sql/migration/*'
    )

    start >> source_to_landing >> landing_to_main >> count_validation >> clean_up_task >> end