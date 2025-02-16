from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import random
import logging
import requests
import time
    
def make_api_call(dag_id: str, dag_run_id: str, task_id: str, try_number: int, retries: int = 3, delay: int = 5):
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
    
    url = f'http://webserver:8080/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{try_number}'
    print(f"url: {url}")

    for attempt in range(retries):
        response = requests.get(
            url,
            params=params,
            cookies=cookies,
            headers=headers,
        )
        if response.status_code == 200:
            return response.text
        else:
            print(f"Attempt {attempt + 1} failed with status code {response.status_code}. Retrying in {delay} seconds...")
            time.sleep(delay)

    return f"Failed to fetch logs after {retries} attempts."

# Fungsi callback yang akan dipanggil saat task gagal
def failure_callback(context):
    dag = context['dag']
    dag_id = dag.dag_id
    dag_run = context['dag_run']
    task_instance = context['task_instance']
    try_number = task_instance.try_number
    task_id = task_instance.task_id

    log = make_api_call(dag_id, dag_run.run_id, task_id, try_number)
    print(f"Response: {log}")
    
# def print_context(context):
#     dag = context['dag']
#     dag_id = dag.dag_id
#     dag_run = context['dag_run']
#     task_instance = context['task_instance']
#     try_number = task_instance.try_number
    
#     print(f"Task ID: {task_instance.task_id}")
#     print(f"DAG ID: {dag_id}")
#     print(f"DAG Run ID: {dag_run.run_id}")
#     print(f"Task Instance Try Number: {try_number}")
    
#     url = f'http://webserver:8080/api/v1/dags/{dag_id}/dagRuns/{dag_run.run_id}/taskInstances/{task_instance.task_id}/logs/{try_number}'
#     print(f"url: {url}")
    
#     response = requests.get(url).text
    
#     print(f"Response: {response}")

# Fungsi Python yang memiliki kemungkinan 50% gagal
def task_with_failure():
    if random.random() < 0.5:
        raise Exception("Task failed randomly!")
    else:
        logging.info("Task succeeded!")

# Default arguments untuk DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'on_failure_callback': failure_callback,  # Callback di tingkat DAG
}

# Membuat DAG
dag = DAG(
    'random_failure_dag',
    default_args=default_args,
    schedule_interval=None,  # DAG ini tidak dijadwalkan, dijalankan manual
    catchup=False,
)

# Task awal (dummy task)
start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

# Task akhir (dummy task)
end_task = DummyOperator(
    task_id='end',
    dag=dag,
)

# Membuat 15 task dengan kemungkinan 50% gagal
tasks = []
for i in range(1, 16):
    task = PythonOperator(
        task_id=f'task_{i}',
        python_callable=task_with_failure,
        dag=dag,
    )
    tasks.append(task)

# Menyusun task secara linear: start -> task_1 -> task_2 -> ... -> task_15 -> end
start_task >> tasks[0]
for i in range(len(tasks) - 1):
    tasks[i] >> tasks[i + 1]
tasks[-1] >> end_task