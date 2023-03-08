import logging
import pandas as pd
from airflow import DAG
from textwrap import dedent
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

def update_table(**kwargs):
    hook = PostgresHook(postgres_conn_id="postgres_localhost")
    conn = hook.get_conn()
    engine = hook.get_sqlalchemy_engine()
    engine_conn = engine.connect()
    cursor = conn.cursor()
    cursor.execute("select coalesce(max(timestamp),'2000-01-01 00:00:00') from Orders")
    max_timestamp = cursor.fetchone()[0]
    cursor.close()
    df = pd.read_csv("/opt/airflow/dags/store_data.csv")
    df['timestamp']=pd.to_datetime(df['timestamp'])
    df = df[df['timestamp'] > max_timestamp]
    ds = kwargs['logical_date'].strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"\n\nTransactions made:\n{df.to_string(index=False)}\nTotal amount earned between {max_timestamp} - {ds}: ${df['amount'].sum()}")
    df.to_sql(name='orders', schema='public', con=engine_conn, if_exists='append', index=False)
    cursor.close()
    engine_conn.close()
    conn.close()
    if datetime.now().day == (datetime.now() + relativedelta(months=1, day=1, days=-1)).day and datetime.now().hour >= timedelta(hour=22):
        return 'trigger_montly_analytics'

default_args = {
    'owner': 'Mdadilfarooq',
    "email_on_failure":True,
    "email_on_retry":True,
    "email":[""],
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'push_to_postgres',
    description='Reads csv and updates postgres table with new records',
    default_args=default_args,
    start_date=datetime(2023, 2, 4),
    schedule_interval='0 10-22/3 * * *',
    tags=["Project"],
    catchup=True
) as dag:
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_localhost',
        sql='transformations/task1.sql'   
    )
    create_table.doc_md = dedent(
        """
        Checks if the table exists, If table doesn't exists creates new table
        """
    )
    update_table = BranchPythonOperator(
        task_id='update_table',
        python_callable=update_table
    )
    update_table.doc_md = dedent(
        """
        Updates the table with new records
        """
    )
    trigger_montly_analytics = TriggerDagRunOperator(
        task_id="trigger_montly_analytics",
        trigger_dag_id="montly_analytics",
        wait_for_completion=False
    )
    trigger_montly_analytics.doc_md = dedent(
        """
        Triggers montly_analytics plot
        """
    )
    create_table >> update_table >> trigger_montly_analytics
