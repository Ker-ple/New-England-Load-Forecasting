import httpx
import pandas as pd
import json
import os
import pg8000.native

conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

DDL = """CREATE TABLE IF NOT EXISTS weather_forecast (
    forecast_id SERIAL PRIMARY KEY,
    forecasted_at TIMESTAMP WITH TIME ZONE,
    forecast_for TIMESTAMP WITH TIME ZONE, 
    forecast_load_mw INTEGER,
    native_load_mw INTEGER,
    UNIQUE(load_datetime)
    );"""

conn.run(DDL)

def lambda_handler(event, context):
    print(event)

    api_key = os.environ.get('WEATHER_AUTH')
    base_url = os.environ.get('PIRATE_FORECAST_API')

    data = get_data(event['latitude'], event['longitude'], base_url=base_url, api_key=api_key, event['variables_map'])    
    data_json = data.to_dict('records')

    for row in data_json:
        cols = ', '.join(f'"{k}"' for k in row.keys())   
        vals = ', '.join(f':{k}' for k in row.keys())
        excluded = ', '.join(f'"EXCLUDED.{k}"' for k in row.keys())
        stmt = f"""INSERT INTO weather_forecast ({cols}) VALUES ({vals}) 
                    ON CONFLICT (weather_datetime) 
                    DO UPDATE SET 
                    ({cols}) = ({excluded});"""
        conn.run(stmt, **row)

    return json.dumps({
        'response': 200,
        'script_name': os.path.basename(__file__),
        'message': 'data sent to postgres',
        'first_data_point': data_json[0],
        'last_data_point': data_json[-1]
    })

def get_data(latitude, longitude, base_url, api_key, **kwargs):
    default_vars_map = {
        'temperature': 'avg_air_temp_hr',
        'apparentTemperature': 'feels_like_temp',
        'humidity': 'rel_humidity_avg_hr',
        'precipAccumulation': 'ppt_total'
        }
    variables_map = kwargs.get('variables_map', default_vars_map)
    raw_data = get_forecast_weather(latitude, longitude, base_url, api_key)
    data = extract_forecast_weather(raw_data, variables_map)
    return data

def get_forecast_weather(latitude, longitude, base_url, api_key):
    resp = httpx.get(url=base_url+api_key+'/'+str(latitude)+','+str(longitude)+'?exclude=currently,minutely,daily&extend=hourly', timeout=None)
    return resp.text

def extract_forecast_weather(raw_weather_data, variables_map):
    data = pd.json_normalize(json.loads(raw_weather_data)['hourly']['data'])
    data = data[variables_map.keys()]
    data.rename(columns=variables_map, inplace=True)
    return data