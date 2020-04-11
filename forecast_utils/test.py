import pytest
import requests

## Se prueba la conexión a la api 2 mediante una solicitud y comprobando el codigo de estado.
def test_api2():
	url = 'http://localhost:8082/v2/24'
	solicitud = requests.get(url)
	assert solicitud.status_code == 200

## De forma similar al test anterior se prueba la conexion a la api 1.
def test_api1():
	url = 'http://localhost:8888/arima/24'
	solicitud = requests.get(url)
	assert solicitud.status_code == 200