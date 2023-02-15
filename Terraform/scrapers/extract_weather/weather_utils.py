import httpx
import pandas as pd
import json
from datetime import datetime

# We're requesting only hourly data, and in the case of forecasts, 168 hours into the future.

def get_weather(latitude, longitude, timestamp):
    is_historic = timestamp < datetime.now().timestamp()
    if is_historic:
        raw_data = get_historic_weather(latitude, longitude, timestamp)
        data = extract_historic_weather(raw_data)
    else:
        raw_data = get_forecast_weather(latitude, longitude, timestamp)
        data = extract_forecast_weather(raw_data)

    return data

def get_historic_weather(latitude, longitude, timestamp):
    base_url = "https://timemachine.pirateweather.net/forecast/"
    resp = httpx.get(url=base_url+api_key+'/'+str(latitude)+','+str(longitude)+','+str(timestamp)+'?exclude=currently,daily'+'&extend=hourly', timeout=None)
    return resp.text

def extract_historic_weather(raw_weather_data):
    data = pd.json_normalize(json.loads(raw_weather_data)['hourly']['data'])
    data['datetime'] = pd.to_datetime(data['time'], unit='s')
    return data

def get_forecast_weather(latitude, longitude, timestamp):
    base_url = "https://api.pirateweather.net/forecast/"
    resp = httpx.get(url=base_url+api_key+'/'+str(latitude)+','+str(longitude)+','+str(timestamp)+'?exclude=currently,minutely,daily'+'&extend=hourly')
    return resp.text

def extract_forecast_weather(raw_weather_data):
    data = pd.json_normalize(json.loads(raw_weather_data)['hourly']['data'])
    data['datetime'] = pd.to_datetime(data['time'], unit='s')
    return data