import httpx
import pandas as pd
import json
import os
import pg8000.native
from datetime import datetime, timezone, timedelta

"""
Example JSON input:
{
    "date_begin": "20220811",
    "date_end": "20220909"
}
"""

"""
Example JSON output: 
{
    "results": [
        {   
            "input": {
                "date_begin": "20220811",
                "date_end": "20220909"
            }
            "script_name": "extract_load_forecast.py",
            "status": "success"
        }
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

DDL = """CREATE TABLE IF NOT EXISTS iso_ne_load (
    load_id SERIAL PRIMARY KEY,
    load_datetime TIMESTAMP WITH TIME ZONE,
    actual_load_mw INTEGER, 
    forecast_load_mw INTEGER,
    native_load_mw INTEGER,
    UNIQUE(load_datetime)
    );"""

conn.run(DDL)

def lambda_handler(event, context):
    print(event)

    base_url = os.environ.get('ISO_NE_API')
    auth = {"Authorization": os.environ.get('ISO_NE_AUTH')}

    data = get_data(event['date_begin'], event['date_end'], base_url, auth)
    data_json = data.to_dict('records')

    print(data_json[0])

    # requests historical load forecast data for each YYYYMMDD date, then concats the results into a tall dataframe 
    
    for row in data_json:
        cols = ', '.join(f'"{k}"' for k in row.keys())   
        vals = ', '.join(f':{k}' for k in row.keys())
        excluded = ', '.join(f'EXCLUDED.{k}' for k in row.keys())
        stmt = f"""INSERT INTO iso_ne_load ({cols}) VALUES ({vals}) 
                    ON CONFLICT (load_datetime) 
                    DO UPDATE SET 
                    ({cols}) = ({excluded});"""
        conn.run(stmt, **row)

    results = {
        "input": event,
        "script_name": os.path.basename(__file__),
        "status": "success"
    }

    # a success returns the .py file name and the first and last data point
    return {
        "results": results
    }

def define_yyyymmdd_date_range(start, end):
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]

def get_data(start_date, end_date, base_url, auth):
    # requests historical load data for each YYYYMMDD date, then concats the results into a tall dataframe
    date_range = define_yyyymmdd_date_range(start_date, end_date)

    # The following block of code allows for automatic retrying of queries that faile due to a RemoteProtocolError. 
    # A request is made for each date in date_range, and failures are appended to a list 'retries'.
    # date_range becomes retries after all requests in date_range have been made, and then requests are made for all dates in date_range.
    # This process repeats 3 times at maximum.
    resp_list = list()
    attempts = 0
    with httpx.Client(headers=auth) as client:
        while attempts < 3:
            retries = list()
            for date in date_range:
                try:
                    r = client.get(url = base_url+'/hourlyloadforecast/day/'+date+'.json', timeout=30)
                    resp_list.append(r.json())
                    print(f"response code for {date}: ", r)
                # you might get this error when using httpx.Client, so we put the failed attempts in a list to try again later
                except httpx.RemoteProtocolError:
                    retries.append(date)
                    print(f"RME for {date} ")
            date_range = retries
            attempts += 1 

    df_list = [pd.json_normalize(json['HourlyLoadForecasts']['HourlyLoadForecast'], sep='_') for json in resp_list]
    final_df = pd.concat(df_list, ignore_index=True, axis=0)

    # renames columns and changes data types as needed, creates a single table for both forecasted and actual load 
    final_df = final_df[['BeginDate', 'LoadMw']]
    final_df = final_df.rename({'LoadMw': 'forecast_load_mw', 'BeginDate': 'load_datetime'}, axis=1)
    final_df = final_df.round({'forecast_load_mw': 0})
    final_df = final_df.astype({'forecast_load_mw': 'int16'})
    return final_df
    