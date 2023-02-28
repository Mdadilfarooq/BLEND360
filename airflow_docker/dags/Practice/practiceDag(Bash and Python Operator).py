from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
default_args = {
    'owner': 'Mdadilfarooq',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

def greet(ti):
    print(f"Hi {ti.xcom_pull(task_ids='get_details', key='name')}, you are {ti.xcom_pull(task_ids='get_details')} years old")

def get_details(ti):
    ti.xcom_push(key='name', value='Adil')
    return 20

def get_version():
    import matplotlib
    print(f'matplotlib: {matplotlib.__version__}')

with DAG(
    dag_id='bash_pyhtonOperator',
    start_date=datetime(2023,2,4,2),
    schedule_interval='@daily',
    default_args=default_args,

    # By default it is True
    catchup=False
) as dag:
    # task1 = BashOperator(
    #     task_id='first_task',
    #     bash_command="echo $((4+10)),"
    # )
    task2 = PythonOperator(
        task_id='matplotlib',
        python_callable=get_version
    )
    task3 = PythonOperator(
        task_id='greet',
        python_callable=greet,
        # op_kwargs={'name':'Adil'}
    )
    task4 = PythonOperator(
        task_id='get_details',
        python_callable=get_details
    )
    task2
    task4 >> task3
# Return value of every func is pushed to xcoms

# To rebuild container with required requirments
# docker build . --tag extending_airflow:latest

# Rebuild airflow webserver and container
# docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler