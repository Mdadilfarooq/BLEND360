from datetime import datetime, timedelta
import csv
import logging
from tempfile import NamedTemporaryFile
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
default_args = {
    'owner': 'Mdadilfarooq',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def postgres_to_s3(ds_nodash, next_ds_nodash):
    hook = PostgresHook(postgres_conn_id="postgres_localhost")
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("select * from my_table where dt >= %s and dt < %s",(ds_nodash, next_ds_nodash))
    with NamedTemporaryFile(mode='w', suffix=f"{ds_nodash}") as f:
    # with open(f"dags/get_my_table_{ds_nodash}.txt","w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)
        f.flush()
        cursor.close()
        conn.close()
        logging.info("Saved my_table data in text file: %s", f"dags/get_my_table_{ds_nodash}.txt")
        s3_hook = S3Hook(aws_conn_id="s3_conn")
        s3_hook.load_file(
            filename=f.name,
            key=f"my_table/{ds_nodash}.txt",
            bucket_name="airflow",
            replace=True
        )
        logging.info("my_table file %s has been pushed to S3!", f.name)
with DAG(
    dag_id='dagPostgresHook',
    default_args=default_args,
    start_date=datetime(2023, 2, 4),
    schedule_interval='0 0 * * *'
) as dag:
    task1 = PythonOperator(
        task_id='postgres_to_s3',
        python_callable=postgres_to_s3
    )
    task1