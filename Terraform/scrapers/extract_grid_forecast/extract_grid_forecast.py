import httpx
import pandas as pd
import json
import os
import pg8000.native
from datetime import datetime, timezone, timedelta

"""
Example JSON input:
{
    'date_begin': '20220221', 
    'date_end': '20220308', 
}
"""

"""
Example JSON output: 
{
    "results": [
        {   
            "input": {
                'date_begin': '20220221', 
                'date_end': '20220308', 
            },
            "script_name": "extract_grid_forecast.py",
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

def lambda_handler(event, context):
    print(event)

    base_url = os.environ.get('ISO_NE_API')
    auth = {"Authorization": os.environ.get('ISO_NE_AUTH')}

    raw_data = get_forecast(event['date_begin'], event['date_end'], base_url=base_url, auth=auth)
    data = clean_data(raw_data)
    data_json = data.to_dict('records')

    print(data_json[0])

    # requests historical load data for each YYYYMMDD date, then concats the results into a tall dataframe 
    
    for row in data_json:
        cols = ', '.join(f'"{k}"' for k in row.keys())   
        vals = ', '.join(f':{k}' for k in row.keys())
        excluded = ', '.join(f'EXCLUDED.{k}' for k in row.keys())
        stmt = f"""INSERT INTO grid_forecast ({cols}) VALUES ({vals});"""
        conn.run(stmt, **row)

    # a success returns the .py file name and the first and last data point
    return {
        "input": event,
        "script_name": os.path.basename(__file__),
        "status": "success"
    }

def define_yyyymmdd_date_range(start, end):
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]

def get_forecast(date_begin, date_end, base_url, auth):
    # requests historical load data for each YYYYMMDD date, then concats the results into a tall dataframe
    # starts by building the range of dates to query    
    date_range = define_yyyymmdd_date_range(date_begin, date_end)

    # The following block of code allows for automatic retrying of failed requests. 
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
                    r = client.get(url = base_url+'/hourlyloadforecast/day/'+date+'.json', timeout=None)
                    resp_list.append(r.json())
                    print(f"response code for {date}: ", r.status_code)
                # you might get errors, so we put the failed attempts in a list to try again later
                except Exception:
                    print(f"error for: {date}")
                    retries.append(date)
                    continue
            date_range = retries   
            attempts += 1
            
    return resp_list

def clean_data(json_list):
    # cleans result of get_load. 
    df_list = [pd.json_normalize(json['HourlyLoadForecasts']['HourlyLoadForecast'], sep='_') for json in json_list]
    df = pd.concat(df_list, ignore_index=True, axis=0)

    # renames columns and changes data types as needed, creates a single table for both forecasted and actual load 
    df = df[['BeginDate', 'CreationDate', 'LoadMw']]
    df = df.rename({'LoadMw': 'load_mw', 'BeginDate': 'forecasted_for', 'CreationDate': 'forecasted_at'}, axis=1)
    return df
    