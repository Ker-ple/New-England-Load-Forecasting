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
	weather_id integer PRIMARY KEY,
	weather_datetime TIMESTAMP WITH TIME ZONE,
	NH_Durham_SSW_air_temp REAL,
	NH_Durham_SSW_ppt_total REAL,
	NH_Durham_SSW_rel_humidity REAL,
	NH_Durham_N_air_temp REAL,
	NH_Durham_N_ppt_total REAL,
	NH_Durham_N_rel_humidity REAL,
	RI_Kingston_W_air_temp REAL,
	RI_Kingston_W_ppt_total REAL,
	RI_Kingston_W_rel_humidity REAL,
	RI_Kingston_NW_air_temp REAL,
	RI_Kingston_NW_ppt_total REAL,
	RI_Kingston_NW_rel_humidity REAL,
	UNIQUE(weather_datetime)
	);"""

conn.run(DDL)

def lambda_handler(event, context):
    print(event)
    variables_map = event['variables_map']
    
    data = read_uscrn(event['uscrn_station_url'], event['date_begin'], event['date_end'], variables_map=variables_map)
    data_json = data.to_dict('records')

    for row in data_json:
        cols = ', '.join(f'"{k}"' for k in row.keys())   
        vals = ', '.join(f':{k}' for k in row.keys())
        excluded = ', '.join(f'"EXCLUDED.{k}"' for k in row.keys())
        stmt = f"""INSERT INTO weather_data ({cols}) VALUES ({vals}) 
                    ON CONFLICT (weather_datetime) 
                    DO UPDATE SET 
                    ({cols}) = ({excluded});"""
        conn.run(stmt, **row)

    return json.dumps({
        'response': 200,
        'script_name': os.path.basename(__file__),
        'message': 'data sent to postgres',
        'first_data_point': data_json[0],
        'last_data_point': data_json[-1],
        'date_start': event['date_start'],
        'date_end': event['date_end'],
        'filter_cols': event['variables_map']
    })