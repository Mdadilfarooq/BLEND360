import io
import csv
import pandas as pd
from airflow import DAG
from textwrap import dedent
import matplotlib.pyplot as plt
from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.email_operator import EmailOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    'owner': 'Mdadilfarooq',
    "email_on_failure":True,
    "email_on_retry":True,
    "email":[""],
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def postgres_to_s3(**kwargs):
    hook = PostgresHook(postgres_conn_id="postgres_localhost")
    conn = hook.get_conn()
    cursor = conn.cursor()
    payment_options = ['cash', 'credit_card', 'debit_card']
    month = kwargs['logical_date'].month
    year = kwargs['logical_date'].year
    for i in payment_options:
        cursor.execute(f"select * from orders where payment_option = '{i}' and extract(month from timestamp) = {month} and extract(year from timestamp) = {year}")
        with NamedTemporaryFile(mode='w', suffix=f"{i}.{month}.{year}") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([i[0] for i in cursor.description])
            csv_writer.writerows(cursor)
            f.flush()
            s3_hook = S3Hook(aws_conn_id="s3_conn")
            s3_hook.load_file(
                filename=f.name,
                key=f"{i}.{month}.{year}.csv",
                bucket_name="airflow",
                replace=True
            )
    cursor.close()
    conn.close()

def plot_pie_chart(**kwargs):
    s3 = S3Hook(aws_conn_id='s3_conn')
    month = kwargs['logical_date'].month
    year = kwargs['logical_date'].year
    list = ['cash', 'debit_card', 'credit_card']
    sum = []
    for i in list:
        s3_object = s3.get_key(f'{i}.{month}.{year}.csv', bucket_name='airflow')
        contents = s3_object.get()['Body'].read().decode('utf-8')
        df = pd.read_csv(io.StringIO(contents))
        month_total = df['amount'].sum()
        if month_total == 0:
            pass
        else:
            df['amount']=df['amount'].str[1:].astype("float")
            month_total = df['amount'].sum()
        sum.append(month_total)
    plt.pie(sum, labels = list, startangle=90, shadow=True, explode=(0.1, 0.1, 0.1), autopct='%1.1f%%')
    plt.title('Analytics')
    temp_file = NamedTemporaryFile(prefix='my_plot', suffix='.png')
    plt.savefig(temp_file.name)
    s3_hook = S3Hook(aws_conn_id="s3_conn")
    s3_hook.load_file(
        filename=temp_file.name,
        key=f"plot.{month}.{year}.png",
        bucket_name="airflow",
        replace=True
    )

with DAG(
    dag_id='montly_analytics',
    default_args=default_args,
    start_date=datetime(2023, 2, 4),
    schedule_interval=None,
    tags=["Project"],
    catchup=False
) as dag:
    postgres_to_s3 = PythonOperator(
        task_id='postgres_to_s3',
        python_callable=postgres_to_s3
    )
    postgres_to_s3.doc_md = dedent(
        """
        Uploads necessary data to S3 bucket
        """
    )
    plot_pie_chart = PythonOperator(
        task_id='plot_pie_chart',
        python_callable=plot_pie_chart,
        provide_context=True
    )
    plot_pie_chart.doc_md = dedent(
        """
        Plots a pie chart sorting total sales based on payment_method
        """
    )
    notify = EmailOperator(
        task_id='notify',
        to="",
        subject="Your montly plots are ready",
        html_content="""
            <h1>Wohoo Done</h1>
        """
    )
    notify.doc_md = dedent(
        """
        Sends an email notification
        """
    )
    postgres_to_s3 >> plot_pie_chart >> notify





