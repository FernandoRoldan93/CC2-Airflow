import Forecast
from datetime import datetime, timedelta
from bson import json_util
import pandas as pd
import json

forecast = Forecast.Forecast()
fc_hum, fc_temp = forecast.predict_weather_ARIMA(24)

horas = pd.date_range(datetime.now(), periods=24, freq="H")
list_horas = []
for hora in horas:
	list_horas.append(hora.strftime('%Y/%m/%d:%H/%M/%S'))


df = pd.DataFrame(list(zip(list_horas, fc_hum, fc_temp)), columns = ['Hora', 'Hum', 'Temp'])

df = df.T

json_dum =df.to_json()
print(json_dum)

#result = {"hora": horas, "temperatura": list(fc_temp), "humedad": list(fc_hum)}

#json_dum = json.dumps(result, default=json_util.default, indent=1)

#holi = json.loads(json_dum)
#print(json_dum)







#forecast = Forecast.Forecast()
#fc_hum, fc_temp = forecast.predict_weather_ARIMA(48)
#print(fc_hum)