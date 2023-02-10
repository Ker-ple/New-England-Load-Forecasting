import httpx
import pandas as pd
import json
import os
import pg8000.native

def lambda_handler(event, context):
    conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

    request = event

    base_url = 'https://webservices.iso-ne.com/api/v1.1'

    requests = {
        'forecast': '/hourlyloadforecast/day/',
        'load': '/hourlysysload/day/'
    }

    auth = {"Authorization": on.environ.get('ISO_NE_AUTH')}

    date_range = define_yyyymmdd_date_range(request['date_begin'], request['date_end'])
    
    resp_list = list()
    for date in date_range:
        resp_list.append(httpx.get(url = base_url+requests[request['request_type']]+date+'.json', headers=auth, timeout=None).json())
    if request['request_type'] == 'forecast':
        df_list = [pd.json_normalize(json['HourlyLoadForecasts']['HourlyLoadForecast'], sep='_') for json in resp_list]
    elif request['request_type'] == 'load':        
        df_list = [pd.json_normalize(json['HourlySystemLoads']['HourlySystemLoad'], sep='_') for json in resp_list]
    final_df = pd.concat(df_list, ignore_index=True, axis=0)

    if request['request_type'] == 'forecast':
        final_df = final_df[['BeginDate', 'LoadMw']]
        final_df.rename({'LoadMw': 'forecast_load_mw', 'BeginDate': 'forecast_datetime'}, axis=1, inplace=True)
        final_df = final_df.round({'forecast_load_mw': 0})
        final_df = final_df.astype({'forecast_load_mw': 'int16'})
        final_json = final_df.to_dict('records')
        DDL = """CREATE TABLE IF NOT EXISTS iso_ne_load (
            forecast_datetime TIMESTAMP WITH TIME ZONE, 
            forecast_load_mw INTEGER
            )"""
        conn.run(DDL)
        print('created forecast table')
        table = 'iso_ne_forecast'
        for row in final_json:
            cols = ', '.join(f'"{k}"' for k in row.keys())   
            vals = ', '.join(f':{k}' for k in row.keys()) 
            stmt = f"""INSERT INTO "{table}" ({cols}) VALUES ({vals})"""
            conn.run(stmt, **row)
        print('uploaded forecast data')
    
    elif request['request_type'] == 'load':
        final_df = final_df[['BeginDate', 'Load', 'NativeLoad']]
        final_df.rename({'Load': 'load_mw', 'NativeLoad': 'native_load_mw', 'BeginDate': 'load_datetime'}, axis=1, inplace=True)
        final_df = final_df.round({'load_mw': 0, 'native_load_mw': 0})
        final_df = final_df.astype({'load_mw': 'int16', 'native_load_mw': 'int16'})
        final_json = final_df.to_dict('records')
        DDL = """CREATE TABLE IF NOT EXISTS iso_ne_load (
            load_datetime TIMESTAMP WITH TIME ZONE, 
            load_mw INTEGER,
            native_load_mw INTEGER
            )"""
        conn.run(DDL)
        print('created load table')
        table = 'iso_ne_load'
        for row in final_json:
            cols = ', '.join(f'"{k}"' for k in row.keys())   
            vals = ', '.join(f':{k}' for k in row.keys()) 
            stmt = f"""INSERT INTO "{table}" ({cols}) VALUES ({vals})"""
            conn.run(stmt, **row)
        print('uploaded load data')

    conn.close()

    return json.dumps({
        'response': 200,
        'message': 'data successfully sent to postgres',
        'first_data_point': final_json[0],
        'last_data_point': final_json[-1]}
        )

def define_yyyymmdd_date_range(start, end):
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]