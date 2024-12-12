from airflow.sensors.base import BaseSensorOperator
from airflow.utils.db import provide_session
from airflow.models import DagRun
from sqlalchemy import Date

class LatestStatusSensor(BaseSensorOperator):
    def __init__(self, external_dag_id, external_task_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.external_dag_id = external_dag_id
        self.external_task_id = external_task_id

    @provide_session
    def poke(self, context, session=None):
        execution_date = context['execution_date']
        
        # Get latest DagRun for the external DAG on the same date
        latest_run = session.query(DagRun)\
            .filter(
                DagRun.dag_id == self.external_dag_id,
                DagRun.execution_date.cast(Date) == execution_date.date()
            )\
            .order_by(DagRun.execution_date.desc())\
            .first()

        if not latest_run:
            return False

        # Check if task is successful
        task_instance = latest_run.get_task_instance(self.external_task_id)
        if not task_instance:
            return False

        return task_instance.state == 'success'
