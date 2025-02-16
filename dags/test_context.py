from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.models.variable import Variable
import requests
import json
from pprint import pprint
import pendulum
import random

localtz = pendulum.timezone("Asia/Jakarta")
timestamp_ms = Variable.get('last_fetch_time')
tables = ['dim_album', 'dim_song', 'dim_artist', 'fact_history']

default_args = {
    'owner': 'rahmadiyan',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 2, tzinfo=localtz),
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
    
def make_api_call(dag_id: str, dag_run_id: str, task_id: str, try_number: int):
    cookies = {
        'mongo-express': 's%3AgJBf6YX2eaUl-URVcVnR7LHsaUs7J16i.Jct2ln%2Bt8onAETCJwHJo4vBZDUdhQp0%2BL6gHQnAfg1k',
        '_xsrf': '2|1d426a80|600861ddcaf165007c1a57d81444fefa|1729914503',
        'next-auth.callback-url': 'http%3A%2F%2Flocalhost%3A3000',
        'next-auth.csrf-token': '1162f15959f40511e9825d28191669bd462c783a7156745fe4ddcb34875c8f35%7C67272e1a4afa36e4f5ebdc99d6fb96ec5c4c65020337951451e7161626ebce93',
        'session': 'b5e244d3-5bc0-4482-a346-569c1e0a72d5.i_QjyiZfxOYzVGI_FnsmTOk2jBA',
    }

    headers = {
        'Accept': 'text/plain',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'mongo-express=s%3AgJBf6YX2eaUl-URVcVnR7LHsaUs7J16i.Jct2ln%2Bt8onAETCJwHJo4vBZDUdhQp0%2BL6gHQnAfg1k; _xsrf=2|1d426a80|600861ddcaf165007c1a57d81444fefa|1729914503; next-auth.callback-url=http%3A%2F%2Flocalhost%3A3000; next-auth.csrf-token=1162f15959f40511e9825d28191669bd462c783a7156745fe4ddcb34875c8f35%7C67272e1a4afa36e4f5ebdc99d6fb96ec5c4c65020337951451e7161626ebce93; session=b5e244d3-5bc0-4482-a346-569c1e0a72d5.i_QjyiZfxOYzVGI_FnsmTOk2jBA',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Referer': f'http://localhost:8081/dags/{dag_id}/grid?dag_run_id={dag_run_id}&tab=logs&task_id={task_id}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    params = {
        'full_content': 'false',
    }

    response = requests.get(
        f'http://webserver:8080/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{try_number}',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    
    return response.text
    
def print_context(**context):
    if random.random() < 0.9:
        dag = context['dag']
        dag_id = dag.dag_id
        dag_run = context['dag_run']
        task_instance = context['task_instance']
        try_number = task_instance.try_number
        task_id = task_instance.task_id
        
        response = make_api_call(dag_id, dag_run.run_id, task_id, try_number)
        pprint(f"Response: {response}")
        raise ValueError("Random number is less than 0.9")
    dag = context['dag']
    dag_id = dag.dag_id
    dag_run = context['dag_run']
    task_instance = context['task_instance']
    try_number = task_instance.try_number
    task_id = task_instance.task_id
    
    response = make_api_call(dag_id, dag_run.run_id, task_id, try_number)
    pprint(f"Response: {response}")

with DAG(
    'context',
    default_args=default_args,
    description='DAG to fetch recent played songs from Flask API and load to main DB',
    schedule_interval='@hourly',
    concurrency=1,
    max_active_runs=1,
    catchup=False,
    tags=['hourly'],
) as dag:

    start = EmptyOperator(task_id='start')
    
    context_task = PythonOperator(
        task_id='testing_context',
        provide_context=True,
        python_callable=print_context,
        dag=dag,
    )
    
    end = EmptyOperator(task_id='end')
    
    start >> context_task >> end