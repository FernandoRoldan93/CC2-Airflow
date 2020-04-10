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



##Inicialización del grafo DAG de tareas para el flujo de trabajo
dag = DAG(
    'practica2_tiempo',
    default_args=default_args,
    description='Grafo de tareas de la practica 2 de Cloud Computing',
    schedule_interval=timedelta(days=1),
)

## Esta tarea es la encargada de limpiar el directorio donde se almacenaran todos los archivos necesarios
PrepararEntorno = BashOperator(
				task_id='PrepararEntorno',
				depends_on_past=False,
				bash_command='rm -r /tmp/workflow/ ; mkdir /tmp/workflow/',
				dag=dag
				)

## En esta tarea se construye el contenedor de la base de datos a partir del archivo docker-compose.yml
CreaDB = BashOperator(
				task_id='CreaDB',
				depends_on_past=False,
				bash_command='docker-compose -f /tmp/workflow/repo/docker-compose.yml up --build -d mongodb',
				dag=dag
				)

## En este caso, se descarga la información referente a la humedad
CapturaDatosHum = BashOperator(
				task_id='CapturaDatosHum',
				depends_on_past=False,
				bash_command='wget --output-document /tmp/workflow/humidity.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/humidity.csv.zip',
				dag=dag
				)

## Al igual que en el caso anterior, se descarga la información referente a la temperatura
CapturaDatosTemp = BashOperator(
				task_id='CapturaDatosTemp',
				depends_on_past=False,
				bash_command='wget --output-document /tmp/workflow/temperature.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/temperature.csv.zip',
				dag=dag
				)

## En esta tarea se limpia el directorio temporal donde se almacenara todo y se descarga todo el código de github
CloneGit=BashOperator(
				task_id='CloneGit',
				depends_on_past=False,
				bash_command='rm -rf /tmp/workflow/repo ; mkdir /tmp/workflow/repo ; git clone https://github.com/FernandoRoldan93/CC2-Airflow.git /tmp/workflow/repo',
                dag=dag
				)

## Habiendo descargado antes toda la información referente a la temperatura y la humedad, esta se descomprime ya que viene comprimida en formato .zip
unzip=BashOperator(
				task_id='unzip',
				depends_on_past=False,
				bash_command='unzip -o /tmp/workflow/temperature.csv.zip -d /tmp/workflow ; unzip -o /tmp/workflow/humidity.csv.zip -d /tmp/workflow',
                dag=dag
)

## Se extrae la información de los ficheros de humedad y temperatura para la ciudad de San Francisco y se almacenan en la base de datos
Extraer_datos = PythonOperator(
				task_id='Extraer_datos',
				python_callable=extract_data,
				op_kwargs={},
				dag=dag
				)

## Una vez levantados todos los procesos se testea la conexion a la api 1 y 2
Tests = BashOperator(
                task_id='Tests',	
                depends_on_past=False,
                bash_command='cd /tmp/workflow/repo ; pytest test.py',
                dag=dag
	            )

## Utilizando docker-compose se levanta el contenedor de la api 1, la cual ofrece la predicción de arima
V1 = BashOperator(
				task_id='V1',
				depends_on_past=False,
				bash_command= 'docker-compose -f /tmp/workflow/repo/docker-compose.yml up -d api_v1',
				dag=dag	
				)

## Utilizando docker-compose se levanta el contenedor de la api 2. A diferencia de la api 1 esta hace una llamada a openWeather para obtener la información meteorologica
V2 = BashOperator(
				task_id='V2',
				depends_on_past=False,
				bash_command='docker-compose -f /tmp/workflow/repo/docker-compose.yml up -d api_v2',
				dag=dag	
				)


PrepararEntorno >> [CapturaDatosHum, CapturaDatosTemp, CloneGit, CreaDB]
[CapturaDatosHum, CapturaDatosTemp, CloneGit, CreaDB]>> unzip >> [Extraer_datos, V1, V2] >> Tests

