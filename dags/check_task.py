from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import TaskInstance
from airflow.exceptions import AirflowException

def check_for_failed_tasks(**kwargs):
    """
    This function checks if any tasks in the same DAG run have failed.
    """
    dag_run = kwargs['dag_run']
    task_instances = dag_run.get_task_instances()

    failed_tasks = []
    for ti in task_instances:
        if ti.state == 'failed':
            failed_tasks.append(ti.task_id)

    if failed_tasks:
        print(f"The following tasks have failed: {failed_tasks}")
    else:
        print("All tasks in this DAG run have succeeded.")


def failed_task_def():
    print("This task will fail")
    raise ValueError("This task has failed")

# Define the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

dag = DAG(
    'check_failed_tasks_dag',
    default_args=default_args,
    schedule_interval=None,  # Manual trigger
    catchup=False,
)

# Task to check for failed tasks
check_failed_tasks_task = PythonOperator(
    task_id='check_failed_tasks',
    python_callable=check_for_failed_tasks,
    provide_context=True,
    trigger_rule='all_done',
    dag=dag,
)

failed_task_1 = PythonOperator(
    task_id='failed_task_1',
    python_callable=failed_task_def,
    dag=dag,
)

failed_task_2 = PythonOperator(
    task_id='failed_task_2',
    python_callable=failed_task_def,
    dag=dag,
)

# Example tasks
task_1 = PythonOperator(
    task_id='task_1',
    python_callable=lambda: print("Task 1 executed successfully"),
    dag=dag,
)

task_2 = PythonOperator(
    task_id='task_2',
    python_callable=lambda: print("Task 2 executed successfully"),
    dag=dag,
)

task_3 = PythonOperator(
    task_id='task_3',
    python_callable=lambda: print("Task 3 executed successfully"),
    dag=dag,
)

# Set task dependencies
task_1 >> task_2 >> task_3 >> failed_task_1 >> failed_task_2 >> check_failed_tasks_task