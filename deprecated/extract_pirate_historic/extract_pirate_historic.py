import httpx
import pandas as pd
import json
import os
import pg8000.native
from datetime import datetime, timezone
import aiometer
from time import time

"""
Example array input:
[
    {
        "latitude": 41.4747,
        "longitude": -71.5203,
        "area": "kingston"
    },
    {
        "latitude": 43.1339,
        "longitude": -70.9264,
        "area": "durham"
    }   
]
"""

"""
Example JSON output:
{
    "results": [
        {
            "input": "durham",
            "script_name": "extract_weather_forecast.py",
            "status": "success"
        },
        .
        .
        .
    ]
}
"""

conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

def lambda_handler(event, context):
    print(event)

    results = list()

    for record in event:
        api_key = os.environ.get('PIRATE_WEATHER_AUTH')
        base_url = os.environ.get('PIRATE_HISTORIC_API')

        data = get_data(record['latitude'], record['longitude'], base_url=base_url, api_key=api_key, forecast_area=record['area'])    
        data_json = data.to_dict('records')
        print(data_json[0])

        for row in data_json:
            cols = ', '.join(f'"{k}"' for k in row.keys())   
            vals = ', '.join(f':{k}' for k in row.keys())
            excluded = ', '.join(f'"EXCLUDED.{k}"' for k in row.keys())
            stmt = f"""INSERT INTO weather_forecasts ({cols}) VALUES ({vals})"""
            conn.run(stmt, **row)
        
        results.append({
            "input": record,
            "script_name": os.path.basename(__file__),
            "status": "success"
        })

    return {
        "results": results
    }

def make_urls()

async def scrape(url, client):
    response = await client.get(url)
    return response

async def get_data(urls, client):
    _start = time()
    results = await aiometer.run_on_each(
        scrape,
        urls,
        max_per_second = 50
    )
    print(f"finished {len(urls)} requests in {time() - _start:.2f} seconds")
    return results

def get_data(latitude, longitude, base_url, api_key, **kwargs):
    default_vars_map = {
        'temperature': 'air_temp',
        'apparentTemperature': 'apparent_temp',
        'humidity': 'relative_humidity',
        'precipAccumulation': 'total_precipitation',
        'windSpeed': 'wind_speed'
        }

    variables_map = kwargs.get('variables_map', default_vars_map)
    forecast_area = kwargs.get('forecast_area', None)
    raw_data = get_forecast_weather(latitude, longitude, base_url, api_key)
    data = extract_forecast_weather(raw_data, forecast_area, variables_map)
    return data

def get_forecast_weather(latitude, longitude, base_url, api_key):
    with httpx.AsyncClient() as client:
    resp = httpx.get(url=base_url+api_key+'/'+str(latitude)+','+str(longitude)+'?exclude=currently,minutely,daily&extend=hourly&units=si', timeout=None)
    return resp.text

def extract_forecast_weather(raw_weather_data, forecast_area, variables_map):
    data = pd.json_normalize(json.loads(raw_weather_data)['hourly']['data'])
    forecasted_for = pd.to_datetime(data['time'], unit='s', utc=True)
    data = data.set_index(forecasted_for)
    data = data[variables_map.keys()]
    data['forecast_area'] = forecast_area
    data = data.rename(columns=variables_map)
    data = data.reset_index()
    data = data.rename(columns={'time': 'forecasted_for'})
    data['forecasted_at'] = datetime.now(timezone.utc)
    
    return data