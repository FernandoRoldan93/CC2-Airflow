import os
import json
from flask import Flask, Response, jsonify
import requests

app = Flask(__name__)

@app.route("/v2/<int:intervalo>", methods=['GET'])
def get_prediccion(intervalo):
	#Se construye la URL de la api de openweather
	url = 'http://api.openweathermap.org/data/2.5/forecast?id=' + os.getenv('SAN_FRANCISCO_ID') + '&appid=' + os.getenv('WEATHER_KEY')
	solicitud = requests.get(url)
	data = solicitud.json()

	##Almacenamos la información devuelta (json) en una variable
	prediccion = data['list']
	result=[]
	count=0

	## En función al intervalo que se haya solicitado se construyen el numero de registros necesarios
	if intervalo == 24:
		while count < 9:
			result.append({'hour':prediccion[count]['dt_txt'], 'temperature':prediccion[count]['main']['temp'], 'humidity':prediccion[count]['main']['humidity']})
			count += 1
	elif intervalo == 48:
		while count < 17:
			result.append({'hour':prediccion[count]['dt_txt'], 'temperature':prediccion[count]['main']['temp'], 'humidity':prediccion[count]['main']['humidity']})
			count += 1
	elif intervalo == 72:
		while count < 25:
			result.append({'hour':prediccion[count]['dt_txt'], 'temperature':prediccion[count]['main']['temp'], 'humidity':prediccion[count]['main']['humidity']})
			count += 1
	else:
		return Response("Petición no valida, el intervalo tiene que ser a 24, 48 o 72 horas", status=400)
	
	## Una vez construida la respuesta se envia con el codigo 200 (OK) y se especifica que el formato es JSON 
	return Response(json.dumps(result), status=200, mimetype="application/json")