from airflow.decorators import dag, task
from datetime import datetime,timedelta
default_args = {
    'owner':'Mdadilfarooq',
    'retries':5,
    'retry_delay':timedelta(minutes=5)
}
@dag(dag_id='taskflowApi',
    default_args=default_args,
    start_date=datetime(2023,2,4),
    schedule_interval='@daily')
def etl():

    # Task Decorator
    @task(multiple_outputs=True)
    def noun():
        return {
            'first_noun': 'adil',
            'second_noun': 'adeeb'
        }

    @task()
    def verb():
        return 'writing'

    @task()
    def sentence(noun1,noun2,verb):
        print(f'{noun1} and {noun2} likes {verb}')
    
    nouns = noun()
    verb = verb()
    sentence(noun1=nouns['first_noun'],noun2=nouns['second_noun'],verb=verb)

test_dag = etl()