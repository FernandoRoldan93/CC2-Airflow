from datetime import timedeltafrom airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.bash_operator import PythonOperator
from airflow.utils.dates import days_ago
import requests


# Inluir biliotecas PIP


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),

}
#Inicialización del grafo DAG de tareas para el flujo de trabajo
dag = DAG(
    'plantilla_p2',
    default_args=default_args,
    description='Un grafo simple de tareas',
    schedule_interval=timedelta(days=1),
)



#def Captura001(url):
#    MF.descargaURL(url, destino)
#    #body=request.get(url)
#    # > fichero /tmp/wor....



PrepararEntorno = BashOperator(
                    task_id='CapturarDatosA',
                    depends_on_past=False,
                    bash_command='mkdir /tmp/workflow/',
                    dag=dag
                    )


CapturaDatosA = BashOperator(
                 task_id='CapturarDatosA',
                 depends_on_past=False,
                 bash_command='wget --output-document /tmp/workflow/humidity.csv.zip  https://github.com/manuparra/MaterialCC2020/blob/master/humidity.csv.zip',
                 dag=dag
                )

CapturaDatosB = BashOperator(
                 task_id='CapturarDatosB',
                 depends_on_past=False,
                 bash_command='curl -o /tmp/workflow/temperature.csv.zip https://github.com/manuparra/MaterialCC2020/blob/master/temperature.csv.zip',
                 dag=dag
                )
                


CapturaDatosB = BashOperator(
                 task_id='CapturarDatosB',
                 depends_on_past=False,
                 bash_command='curl -o /tmp/workflow/temperature.csv.zip https://github.com/manuparra/MaterialCC2020/blob/master/temperature.csv.zip',
                 dag=dag
                )


CapturaCodigoFuenteV1=BashOperator(
                task_id='CapV1',
                depends_on_past=False,
                bash_command='cd /tmp/workflow/;git clone https://git....../mirepo01Practica02.git',
                dag=dag
                )

CapturaCodigoFuenteV2=BashOperator(
                task_id='CapV2',
                depends_on_past=False,
                bash_command='git clone  https://git....../mirepo02Practica02.git /tmp/workflow/',
                dag=dag
                )



#CapturaCodigoFuente=BashOperator(
#                task_id='CapV2',
#                depends_on_past=False,
#                bash_command='sh /tmp/workflow/captura.sh',
#                dag=dag
#                )
          
#CapturaDatosC = PythonOperator(
#                 task_id='CapturarDatosC',
#                 python_callable=Captura001,
#                 op_kwargs={'url': "https://github.com/manuparra/MaterialCC2020/blob/master/solarradiation.csv.zip"}, 
#                 dag=dag
#                )
                

# Aqui creamos el dag de forma 
PrepararEntorno >> [CapturaCodigoFuenteV1, CapturaCodigoFuenteV2] >>  [ CapturaDatosA >> ProcesaDatosA,CapturaDatosB >> ProcesaDatosB ]

