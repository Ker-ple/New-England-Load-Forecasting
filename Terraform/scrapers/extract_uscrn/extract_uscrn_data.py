import httpx
import pg8000.native
from uscrn_utils import *
import os
import json
import pandas as pd

"""
Example JSON Input:
{
    "station_names": ["RI_Kingston_1_NW", "RI_Kingston_1_W"],
    "date_begin": "20220811",
    "date_end": "20230224"
}
"""

"""
Example JSON output:
{
    "results": [
        {
            "input": {
                "station_names": ["RI_Kingston_1_NW", "RI_Kingston_1_W"],
                "date_begin": "20220811",
                "date_end": "20230224"
            },
            "station_name": "RI_Kingston_1_NW",
            "script_name": "extract_uscrn_data.py",
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
    results = list()

    year = pd.to_datetime(record['date_begin'], format='%Y%m%d').year

    for station in event['station_names']:
        try:

            hourly_url, subhourly_url = url_for_station(station, year)

            print("hourly_url: ", hourly_url, '\n', "subhourly_url: ", subhourly_url)

            data_hourly = read_uscrn_hourly(hourly_url, event['date_begin'], event['date_end'])
            data_subhourly = read_uscrn_subhourly(subhourly_url, event['date_begin'], event['date_end'])
            data_joined = data_subhourly.merge(data_hourly, on=['weather_datetime', 'station_name'])
            data_json = data_joined.to_dict('records')

            for row in data_json:
                cols = ', '.join(f'"{k}"' for k in row.keys())   
                vals = ', '.join(f':{k}' for k in row.keys())
                excluded = ', '.join(f'"EXCLUDED.{k}"' for k in row.keys())
                stmt = f"""INSERT INTO weather_data ({cols}) VALUES ({vals});"""
                conn.run(stmt, **row)

            results.append({
                "input": event,
                "station_name": station,
                "script_name": os.path.basename(__file__),
                "status": "success"
            })
        
        except Exception as e:
            results.append({
                "input": event,
                "station_name": station,
                "script_name": os.path.basename(__file__),
                "status": str(e)
            })
        
        return {
            "results": results
        }
        

def url_for_station(station_name, year):
    subhourly = f"https://www1.ncdc.noaa.gov/pub/data/uscrn/products/subhourly01/{year}/CRNS0101-05-{year}-{station_name}.txt"
    hourly = f"https://www1.ncdc.noaa.gov/pub/data/uscrn/products/hourly02/{year}/CRNH0203-{year}-{station_name}.txt"

    return hourly, subhourly