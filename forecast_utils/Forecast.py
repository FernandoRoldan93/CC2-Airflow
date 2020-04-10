import pmdarima as pm
import os
import pickle
import pandas as pd
from pymongo import MongoClient

class Forecast:

	def get_data(self):
		client = MongoClient("mongodb://mongodb:27017/")
		db = client["database"]
		all_data = db.data_records.find_one({'index': 'date'})
		df = pd.DataFrame(all_data['data'])
		client.close()
		return df

	def train_arima(self):
		"""
		Entrena los modelos de arima para temperatura y humedad en 
		este caso no es necesario entrenar el modelo de nuevo si 
		este ha sido creado con anterioridad
		"""

		df = self.get_data()
		
		#Creo el directorio temporal si no existe
		if not os.path.exists('./modelos'):
			os.mkdir('./modelos')

		#Si el modelo de humedad no ha sido creado anteriormente se crea y se almacena
		if not os.path.exists('./modelos/Arima_humidity.pckl'):
			model = pm.auto_arima(df.Humidity, start_p=1, start_q=1,
	                      test='adf',       
	                      max_p=3, max_q=3, 
	                      m=1,              
	                      d=None,           
	                      seasonal=False,   
	                      start_P=0, 
	                      D=0, 
	                      trace=True,
	                      error_action='ignore',  
	                      suppress_warnings=True, 
	                      stepwise=True)
			
			pickle.dump(model, open("./modelos/Arima_humidity.pckl", "wb"))

		#Si el modelo de temperatura no ha sido creado anteriormente se crea y se almacena
		if not os.path.exists('./modelos/Arima_temperature.pckl'):	
			model = pm.auto_arima(df.Temperature, start_p=1, start_q=1,
	                      test='adf',       
	                      max_p=3, max_q=3, 
	                      m=1,              
	                      d=None,           
	                      seasonal=False,   
	                      start_P=0, 
	                      D=0, 
	                      trace=True,
	                      error_action='ignore',  
	                      suppress_warnings=True, 
	                      stepwise=True)
			
			pickle.dump(model, open("./modelos/Arima_temperature.pckl", "wb"))


	def predict_weather_ARIMA(self, intervalo):
		#Si los modelos de temperatura no han sido creados se llama a la funcion que los entrena
		if (not os.path.exists('./modelos/Arima_humidity.pckl') 
			or not os.path.exists('./modelos/Arima_temperature.pckl')):
			self.train_arima()

		#Cargamos el modelo de humedad
		file = open("./modelos/Arima_humidity.pckl", "rb")
		hum = pickle.load(file)
		file.close()
		
		#Cargamos el modelo de temperatura
		file = open("./modelos/Arima_temperature.pckl", "rb")
		temp = pickle.load(file)
		file.close()

		#Realizamos la prediccion llamando a ARIMA
		intervalo = int(intervalo)
		fc_hum = hum.predict(n_periods=intervalo)
		fc_temp = temp.predict(n_periods=intervalo)
		return fc_hum, fc_temp;
