import json
from flask import Flask, Response
import pandas as pd
app = Flask(__name__)

import Forecast

@app.route("/arima/<string:intervalo>", methods=['GET'])
def get_prediccion_arima(intervalo):
	if intervalo not in ['24','48','72']:
		return Response("Petición no valida, el intervalo tiene que ser a 24, 48 o 72 horas", status=400)

	forecast = Forecast.Forecast()
	fc_hum, fc_temp = forecast.predict_weather_ARIMA(intervalo)

	horas = pd.date_range(datetime.now(), periods=intervalo, freq="H")
	list_horas = []
	for hora in horas:
		list_horas.append(hora.strftime('%Y/%m/%d:%H/%M'))


	df = pd.DataFrame(list(zip(list_horas, fc_hum, fc_temp)), columns = ['Hora', 'Hum', 'Temp'])

	df = df.T

	json_dum =df.to_json()


	return Response(json_dum, status=200)