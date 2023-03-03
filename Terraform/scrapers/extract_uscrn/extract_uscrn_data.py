import pg8000.native
from uscrn_utils import *
import os
import pandas as pd
from datetime import datetime

"""
Example JSON Input:
{   
    "area": "kingston",
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
    ],   
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
    station_area VARCHAR,
	air_temp REAL,
    apparent_temp REAL,
	ppt_total REAL,
	relative_humidity REAL,
    wind_speed REAL,
	UNIQUE(weather_datetime, station_name)
	);"""

conn.run(DDL)

def lambda_handler(event, context):
    print(event)
    hourly_dfs = list()
    subhourly_dfs = list()

    date_ranges = split_date(event['date_begin'], event['date_end'])

    for date in date_ranges:
        year = datetime.strptime(date['date_begin'], '%Y%m%d').year

        for station in event['station_names']:
            hourly_url, subhourly_url = url_for_station(station, year)

            print("hourly_url: ", hourly_url, '\n', "subhourly_url: ", subhourly_url)

            data_hourly = read_uscrn_hourly(hourly_url, date['date_begin'], date['date_end'])
            data_subhourly = read_uscrn_subhourly(subhourly_url, date['date_begin'], date['date_end'])
            hourly_dfs.append(data_hourly)
            subhourly_dfs.append(data_subhourly)

    all_hourly = pd.concat(hourly_dfs, ignore_index=True, axis=0)
    all_subhourly = pd.concat(subhourly_dfs, ignore_index=True, axis=0)

    data_joined = all_subhourly.merge(all_hourly, on=['weather_datetime', 'station_name'])
    data_joined['apparent_temp'] = data_joined.apply(lambda x: get_apparent_temp(x['air_temp'], x['relative_humidity'], x['wind_speed']), axis=1)
    data_joined['station_area'] = event['area']
    data_json = data_joined.to_dict('records')
    print(data_json[0])

    for row in data_json:
        cols = ', '.join(f'"{k}"' for k in row.keys())   
        vals = ', '.join(f':{k}' for k in row.keys())
        excluded = ', '.join(f'"EXCLUDED.{k}"' for k in row.keys())
        stmt = f"""INSERT INTO weather_data ({cols}) VALUES ({vals});"""
        conn.run(stmt, **row)

    return {
        "input": event,
        "script_name": os.path.basename(__file__),
        "status": "success"
    }

