from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
from pymongo import MongoClient
import requests

default_args = {
	'owner': 'Fernan',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

#######################################################
def extract_data():
	hum = pd.read_csv("/tmp/workflow/humidity.csv")
	temp = pd.read_csv("/tmp/workflow/temperature.csv")
	hum = hum[['datetime', 'San Francisco']]
	hum = hum.rename(columns = {'San Francisco': 'Humidity'})
	temp = temp[['datetime', 'San Francisco']]
	temp = temp.rename(columns = {'San Francisco': 'Temperature'})
	df = pd.merge(hum, temp, on='datetime')
	df = df.dropna('index')
	df = df.tail(1000)
	insert_data(df)



def insert_data(data):
	client = MongoClient("mongodb://localhost:27017/")
	db = client["database"]
	collection = db["data_records"]
	data_dict = data.to_dict("records")
	collection.insert_one({"index":"date", "data":data_dict})
	client.close()


#######################################################



#Inicialización del grafo DAG de tareas para el flujo de trabajo
dag = DAG(
    'practica2_tiempo',
    default_args=default_args,
    description='Grafo de tareas de la practica 2 de Cloud Computing',
    schedule_interval=timedelta(days=1),
)

PrepararEntorno = BashOperator(
				task_id='Prepara_entorno',
				depends_on_past=False,
				bash_command='rm -r /tmp/workflow/ ; mkdir /tmp/workflow/',
				dag=dag
				)

IniciaDockerDB = BashOperator(
				task_id='Inicia_DB',
				depends_on_past=False,
				bash_command='docker rm -f db ; docker run -d --rm -p 27017:27017 --name db mongo:3',
				dag=dag
				)



CapturaDatosHum = BashOperator(
				task_id='CapturaDatosA',
				depends_on_past=False,
				bash_command='wget --output-document /tmp/workflow/humidity.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/humidity.csv.zip',
				dag=dag
				)

CapturaDatosTemp = BashOperator(
				task_id='CapturarDatosB',
				depends_on_past=False,
				bash_command='wget --output-document /tmp/workflow/temperature.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/temperature.csv.zip',
				dag=dag
				)

CloneGit=BashOperator(
				task_id='Clone_Git',
				depends_on_past=False,
				bash_command='rm -rf /tmp/workflow/repo/ ; mkdir /tmp/workflow/repo ; git clone https://github.com/FernandoRoldan93/CC2-Airflow.git /tmp/workflow/repo',
                dag=dag
				)

unzip=BashOperator(
				task_id='Unzip',
				depends_on_past=False,
				bash_command='unzip -o /tmp/workflow/temperature.csv.zip -d /tmp/workflow ; unzip -o /tmp/workflow/humidity.csv.zip -d /tmp/workflow',
                dag=dag
)

Extraer_datos = PythonOperator(
				task_id='Extraer_almacenar',
				python_callable=extract_data,
				op_kwargs={},
				dag=dag
				)


Build_api1 = BashOperator(
				task_id='Build_api1',
				depends_on_past=False,
				bash_command='cd /tmp/workflow/repo/forecast_utils/ ; docker build --rm -f Dockerfile1 -t api_arima .',
				dag=dag	
				)

V1 = BashOperator(
				task_id='Version1',
				depends_on_past=False,
				bash_command='docker run --rm --name api_arima -v /tmp/modelos/:/tmp/modelos/ -p 8001:8081 api_arima',
				dag=dag	
				)


PrepararEntorno >> [IniciaDockerDB ,CapturaDatosHum, CapturaDatosTemp, CloneGit] >> unzip >> Extraer_datos >> Build_api1 >> V1

