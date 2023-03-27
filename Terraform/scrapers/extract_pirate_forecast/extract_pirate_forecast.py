import httpx
import pandas as pd
import json
import os
import pg8000.native
from datetime import datetime, timezone

conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

def lambda_handler(event, context):
    print(event)

    api_key = os.environ.get('PIRATE_WEATHER_AUTH')
    base_url = os.environ.get('PIRATE_FORECAST_API')

    lat_longs = list()
    for row in conn.run("SELECT DISTINCT latitude, longitude FROM weather_historical;"):
        lat_longs.append(row)
    
    for row in lat_longs:
        lat, lon = row[0], row[1]
        data = get_data(lat, lon, base_url=base_url, api_key=api_key)
        data['longitude'] = lon
        data['latitude'] = lat    
        data_json = data.to_dict('records')
        print(data_json[0])

        for row in data_json:
            cols = ', '.join(f'"{k}"' for k in row.keys())   
            vals = ', '.join(f':{k}' for k in row.keys())
            stmt = f"""INSERT INTO weather_forecast ({cols}) VALUES ({vals});"""
            conn.run(stmt, **row)
            
    return {
        "script_name": os.path.basename(__file__),
        "status": "success"
    }

def get_data(latitude, longitude, base_url, api_key, **kwargs):
    default_vars_map = {
        'temperature': 'air_temperature',
        'apparentTemperature': 'apparent_temperature',
        'humidity': 'relative_humidity',
        'precipAccumulation': 'total_precipitation',
        'windSpeed': 'wind_speed',
        'dewPoint': 'dewpoint_temperature'
        }

    variables_map = kwargs.get('variables_map', default_vars_map)
    with httpx.Client() as client:
        raw_data = get_forecast_weather(latitude, longitude, base_url, api_key, client)
    data = extract_forecast_weather(raw_data, variables_map)
    return data

def get_forecast_weather(latitude, longitude, base_url, api_key, client):
    resp = client.get(url=base_url+api_key+'/'+str(latitude)+','+str(longitude)+'?exclude=currently,minutely,daily&extend=hourly&units=us', timeout=None)
    return resp.json()

def extract_forecast_weather(raw_weather_data, variables_map):
    data = pd.json_normalize(raw_weather_data['hourly']['data'])
    forecasted_for = pd.to_datetime(data['time'], unit='s', utc=True)
    data = data.set_index(forecasted_for)
    data = data[variables_map.keys()]
    data = data.rename(columns=variables_map)
    data = data.reset_index()
    data = data.rename(columns={'time': 'forecasted_for'})
    data['forecasted_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    return data