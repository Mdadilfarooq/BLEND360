from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'Mdadilfarooq',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}
with DAG(
    dag_id='postgresOperator',
    default_args=default_args,
    start_date=datetime(2023, 2, 4),
    schedule_interval='0 0 * * *',
    catchup=True
) as dag:
    task1 = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_localhost',
        sql="""
            create table if not exists my_table(
            dt date,
            dag_id character varying,
            primary key (dt, dag_id)
            ) 
        """
    )
    task3 =PostgresOperator(
        task_id='delete_row_from_table',
        postgres_conn_id='postgres_localhost',
        # airflow macros
        sql="""
            delete from my_table where dt = '{{ds}}' and dag_id = '{{dag.dag_id}}'
        """
    )
    task2 =PostgresOperator(
        task_id='insert_row_into_table',
        postgres_conn_id='postgres_localhost',
        # airflow macros
        sql="""
            insert into my_table (dt,dag_id) values ('{{ds}}','{{dag.dag_id}}')
        """
    )
    task1>>task3>>task2
