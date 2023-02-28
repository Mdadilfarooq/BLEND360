from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.operators.email_operator import EmailOperator

default_args = {
    'owner': 'Mdadilfarooq',
    "email_on_failure":True,
    "email_on_retry":True,
    "email":["adilfarooq0138@gmail.com"],
    'retries': 5,
    'retry_delay': timedelta(minutes=10)
}

with DAG(
    dag_id='minioDag',
    start_date=datetime(2023,2,4),
    schedule_interval='@daily',
    default_args=default_args
) as dag:


    task1 = S3KeySensor(
        task_id='sensor_minio_s3',
        bucket_name='airflow',
        bucket_key='data.csv',
        poke_interval=60,
        timeout=180,
        mode='poke',
        soft_fail=False,
        aws_conn_id='s3_conn'
    )


    notify = EmailOperator(
        task_id='notify',
        to="me20btech11028@iith.ac.in",
        subject="Airflow Success",
        html_content="""
            <h1>test</h1>
        """
    )
    task1>>notify