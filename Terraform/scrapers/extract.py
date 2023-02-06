import httpx
import pandas as pd
import json
import os
import psycopg2
import boto3

conn = psycopg2.connect(
    user = os.environ.get['DB_USERNAME'],
    password = os.environ.get['DB_PASSWORD'],
    host = os.environ.get['DB_HOSTNAME'],
    database = os.environ.get['DB_NAME']
)

def lambda_handler(event, context):
    try:
        request = event

        cursor = conn.cursor()

        base_url = 'https://webservices.iso-ne.com/api/v1.1'

        requests = {
            'forecast': '/hourlyloadforecast/day/',
            'load': '/hourlysysload/day/'
        }

        auth = {'Authorization': 'Basic Y3lydXNraXJidXNAZ21haWwuY29tOkFpNlR5SkM5RGhFUkhh'}

        date_range = define_yyyymmdd_date_range(request['date_begin'], request['date_end'])
        
        resp_list = list()
        for date in date_range:
            resp_list.append(httpx.get(url = base_url+requests[request['request_type']]+date+'.json', headers=auth).json())
        if request['request_type'] == 'forecast':
            df_list = [pd.json_normalize(json['HourlyLoadForecasts']['HourlyLoadForecast'], sep='_') for json in resp_list]
        elif request['request_type'] == 'load':        
            df_list = [pd.json_normalize(json['HourlySystemLoads']['HourlySystemLoad'], sep='_') for json in resp_list]
        final_df = pd.concat(df_list, ignore_index=True, axis=0)

        final_df['date'] = pd.to_datetime(final_df['BeginDate']).dt.strftime('%Y-%m-%d')
        final_df['time'] = pd.to_datetime(final_df['BeginDate']).dt.strftime('%H')

        if request['request_type'] == 'forecast':
            final_df = final_df[['date', 'time', 'LoadMw']]
            final_json = final_df.to_dict('records')
            query1 = """CREATE TABLE IF NOT EXISTS power.iso_ne_forecast
                (
                    forecast_date date
                    forecast_time time
                    forecasted_load_mw integer
                );"""
            query2 = f"INSERT INTO power.iso_ne_forecast {final_json.values()} VALUES"
        
        elif request['request_type'] == 'load':
            final_df = final_df[['date', 'time', 'Load', 'NativeLoad']]
            final_json = final_df.to_dict('records')
            query1 = """CREATE TABLE IF NOT EXISTS power.iso_ne_load
                (
                    load_date date  
                    load_time time
                    load_mw integer  
                    native_load_mw integer
                );"""
            query2 = f"INSERT INTO power.iso_ne_load {final_json.values} VALUES"

        curr.execute(query1)
        curr.execute(query2)
        conn.commit()

        return json.dumps({
            'response': 200,
            'message': 'data successfully sent to postgres'})
    
    except Exception as e:
        return json.dumps({
            'response': 500,
            'message': str(e)}
        )

def define_yyyymmdd_date_range(start, end):
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]