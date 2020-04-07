import pmdarima as pm
import os
import pickle
import pandas as pd
from pymongo import MongoClient

class Forecast:

	def get_data(self):
		client = MongoClient("mongodb://localhost:27017/")
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
		if not os.path.exists('/tmp/workflow/modelos'):
			os.mkdir('/tmp/workflow/modelos')

		if not os.path.exists('/tmp/workflow/modelos/Arima_humidity.pckl'):
			#Entreno el modelo de la humedad y lo guardo
			model = pm.auto_arima(df.Humidity, start_p=1, start_q=1,
	                      test='adf',       # use adftest to find optimal 'd'
	                      max_p=3, max_q=3, # maximum p and q
	                      m=1,              # frequency of series
	                      d=None,           # let model determine 'd'
	                      seasonal=False,   # No Seasonality
	                      start_P=0, 
	                      D=0, 
	                      trace=True,
	                      error_action='ignore',  
	                      suppress_warnings=True, 
	                      stepwise=True)
			
			pickle.dump(model, open("/tmp/workflow/modelos/Arima_humidity.pckl", "wb"))
		
		if not os.path.exists('/tmp/workflow/modelos/Arima_temperature.pckl'):	
			#Entreno el modelo de temperatura y lo guardo
			model = pm.auto_arima(df.Temperature, start_p=1, start_q=1,
	                      test='adf',       # use adftest to find optimal 'd'
	                      max_p=3, max_q=3, # maximum p and q
	                      m=1,              # frequency of series
	                      d=None,           # let model determine 'd'
	                      seasonal=False,   # No Seasonality
	                      start_P=0, 
	                      D=0, 
	                      trace=True,
	                      error_action='ignore',  
	                      suppress_warnings=True, 
	                      stepwise=True)
			
			pickle.dump(model, open("/tmp/workflow/modelos/Arima_temperature.pckl", "wb"))


	def predict_weather_ARIMA(self, intervalo):
		if (not os.path.exists('/tmp/workflow/modelos/Arima_humidity.pckl') 
			or not os.path.exists('/tmp/workflow/modelos/Arima_temperature.pckl')):
			self.train_arima()

		file = open("/tmp/workflow/modelos/Arima_humidity.pckl", "rb")
		hum = pickle.load(file)
		file.close()
		
		file = open("/tmp/workflow/modelos/Arima_temperature.pckl", "rb")
		temp = pickle.load(file)
		file.close()

		fc_hum = hum.predict(n_periods=intervalo)
		fc_temp = temp.predict(n_periods=intervalo)
		return fc_hum, fc_temp;
