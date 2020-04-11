import json
from datetime import datetime
from flask import Flask, Response, jsonify
import pandas as pd
app = Flask(__name__)

import Forecast

@app.route("/arima/<string:intervalo>", methods=['GET'])
def get_prediccion_arima(intervalo):
	## Se comprueba si el intervalo es el correcto, de no ser asi, se devuelve un mensaje de error
	if intervalo not in ['24','48','72']:
		return Response("Petición no valida, el intervalo tiene que ser a 24, 48 o 72 horas", status=400)

	## Se crea un objeto de la clase forecast y se obtiene la prediccion, si el modelo no se ha creado con anterioridad se contruye y se realiza la consulta
	forecast = Forecast.Forecast()
	fc_hum, fc_temp = forecast.predict_weather_ARIMA(intervalo)

	## Se crea una lista de horas que van desde la hora actual hasta el intervalo indicado de hora en hora
	intervalo = int(intervalo)
	horas = pd.date_range(datetime.now(), periods=intervalo, freq="H")
	list_horas = []
	for hora in horas:
		list_horas.append(hora.strftime('%Y.%m.%d:%H.%M'))

	## Se crea la respuesta en formato json
	count = 0
	result = []
	while count < intervalo:
		result.append({'hour':list_horas[count], 'temperature':fc_temp[count], 'humidity':fc_hum[count]})	
		count +=1

	return Response(json.dumps(result, indent=4), 200, mimetype="application/json")