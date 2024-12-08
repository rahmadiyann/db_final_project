from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.models import DagRun
from airflow.utils.db import provide_session
from datetime import datetime, timedelta
import pendulum

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

def get_latest_execution_date(dag_id):
    """Get the execution date of the last successful run for a given dag_id"""
    @provide_session
    def get_date(session=None):
        last_dagrun = session.query(DagRun)\
            .filter(
                DagRun.dag_id == dag_id
            )\
            .order_by(DagRun.execution_date.desc())\
            .first()
        return last_dagrun.execution_date if last_dagrun else None
    return get_date()

def check_last_dagrun(dt):
    """Returns the execution date to look for"""
    latest_date = get_latest_execution_date('spotify_analysis_etl')
    if latest_date:
        return latest_date
    return None

dag = DAG(
    'email_blast',
    default_args=default_args,
    description='Email blast DAG that runs after spotify analysis',
    schedule_interval='@monthly',
    concurrency=1,
    max_active_runs=1,
    catchup=False,
)

start = EmptyOperator(
    task_id='start',
    dag=dag
)

wait_for_spotify = ExternalTaskSensor(
    task_id='wait_for_spotify',
    external_dag_id='spotify_analysis_etl',
    external_task_id='end',
    timeout=3600,
    mode='reschedule',
    allowed_states=['success'],
    failed_states=['failed', 'skipped'],
    execution_date_fn=check_last_dagrun,
    dag=dag
)

end = EmptyOperator(
    task_id='end',
    dag=dag
)

start >> wait_for_spotify >> end
