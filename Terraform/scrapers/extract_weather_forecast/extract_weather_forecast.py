import httpx
import pandas as pd
import json
import os
import pg8000.native
from geopy.geocoders import Nominatim
from datetime import datetime, timezone

conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

DDL = """CREATE TABLE IF NOT EXISTS weather_forecasts (
	forecast_id SERIAL PRIMARY KEY,
	forecasted_at TIMESTAMP WITH TIME ZONE,
    forecasted_for TIMESTAMP WITH TIME ZONE
	air_temp REAL,
    wind_speed REAL,
    apparent_temp REAL,
    ppt_total REAL,
    relative_humidity REAL,
    forecast_area VARCHAR,
    UNIQUE(forecasted_at, forecasted_for, forecast_area)
	);"""

conn.run(DDL)

def lambda_handler(event, context):
    print(event)

    api_key = os.environ.get('WEATHER_AUTH')
    base_url = os.environ.get('PIRATE_FORECAST_API')

    for record in event['records']:

        data = get_data(record['forecast_area'].lower(), base_url=base_url, api_key=api_key)    
        data_json = data.to_dict('records')

        for row in data_json:
            cols = ', '.join(f'"{k}"' for k in row.keys())   
            vals = ', '.join(f':{k}' for k in row.keys())
            excluded = ', '.join(f'"EXCLUDED.{k}"' for k in row.keys())
            stmt = f"""INSERT INTO weather_forecast ({cols}) VALUES ({vals})"""
            conn.run(stmt, **row)

    return json.dumps({
        'response': 200,
        'script_name': os.path.basename(__file__),
        'message': 'data sent to postgres'
    })

def get_data(forecast_area, base_url, api_key, **kwargs):
    default_vars_map = {
        'temperature': 'air_temp',
        'apparentTemperature': 'apparent_temp',
        'humidity': 'rel_humidity',
        'precipAccumulation': 'ppt_total'
        }

    latitude, longitude = get_lat_long(forecast_area) 

    variables_map = kwargs.get('variables_map', default_vars_map)
    raw_data = get_forecast_weather(latitude, longitude, base_url, api_key)
    data = extract_forecast_weather(raw_data, forecast_area, variables_map)
    return data

def get_forecast_weather(latitude, longitude, base_url, api_key):
    resp = httpx.get(url=base_url+api_key+'/'+str(latitude)+','+str(longitude)+'?exclude=currently,minutely,daily&extend=hourly', timeout=None)
    return resp.text

def extract_forecast_weather(raw_weather_data, forecast_area, variables_map):
    data = pd.json_normalize(json.loads(raw_weather_data)['hourly']['data'])
    forecasted_for = pd.to_datetime(data['time'], unit='s', utc=True)
    data = data.set_index(forecasted_for)
    data = data[variables_map.keys()]
    data['forecast_area'] = forecast_area
    data = data.rename(columns=variables_map)
    data = data.reset_index()
    data = data.rename(columns={'index': 'forecasted_for'})
    data['forecasted_at'] = datetime.now(timezone.utc)
    
    return data

def get_lat_long(place):

    place_zipcode_dict = {
        'boston': '02116',
        'durham': '03824',
        'kingston': '02881'
    }

    geolocator = Nominatim(user_agent = "weather_forecast")
    location = geolocator.geocode({'zipcode': place_zip_code_dict[place]})

    return location.latitude, location.longitude