import httpx
import pg8000.native
from uscrn_utils import *
import os
import json

conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

DDL = """CREATE TABLE IF NOT EXISTS weather_data (
	weather_id SERIAL PRIMARY KEY,
	weather_datetime TIMESTAMP WITH TIME ZONE,
    station_name VARCHAR,
	air_temp REAL,
	ppt_total REAL,
	relative_humidity REAL,
    wind_speed REAL,
	UNIQUE(weather_datetime, station_name)
	);"""

conn.run(DDL)

def lambda_handler(event, context):
    print(event)
    variables_map = event['variables_map']
    
    data_hourly = read_uscrn_hourly(event['uscrn_station_url'], event['date_begin'], event['date_end'])
    data_subhourly = read_uscrn_subhourly(event['uscrn_station_url'], event['date_begin'], event['date_end'])
    data_joined = data_subhourly.merge(data_hourly, on=['weather_datetime', 'station_name'])
    data_json = data_joined.to_dict('records')

    for row in data_json:
        cols = ', '.join(f'"{k}"' for k in row.keys())   
        vals = ', '.join(f':{k}' for k in row.keys())
        excluded = ', '.join(f'"EXCLUDED.{k}"' for k in row.keys())
        stmt = f"""INSERT INTO weather_data ({cols}) VALUES ({vals});"""
        conn.run(stmt, **row)

    return json.dumps({
        'response': 200,
        'script_name': os.path.basename(__file__),
        'message': 'data sent to postgres',
        'first_data_point': data_json[0],
        'last_data_point': data_json[-1],
        'date_start': event['date_start'],
        'date_end': event['date_end']
    })