import httpx
import pandas as pd
import json
import os
import pg8000.native
import boto3
from datetime import datetime, timezone, timedelta
from boto3.dynamodb.types import TypeDeserializer

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('lambda_params')
    print('DynamoDB table set.')

    print(event['Records'])

    pertinent_info = [ ddb_deserialize(r["dynamodb"]["OldImage"]) for r in event['Records'] ]
    keys = [ ddb_deserialize(r["dynamodb"]["Keys"]) for r in event['Records'] ]

    conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

    base_url = 'https://webservices.iso-ne.com/api/v1.1'

    auth = {"Authorization": os.environ.get('ISO_NE_AUTH')}

    date_begin = extract_date_from_timestamp(pertinent_info[0]['request_date_begin'])
    date_end = extract_date_from_timestamp(pertinent_info[0]['request_date_end'])

    date_range = define_yyyymmdd_date_range(date_begin, date_end)
    
    resp_list = list()
    for date in date_range:
        resp_list.append(httpx.get(url = base_url+'/hourlysysload/day/'+date+'.json', headers=auth, timeout=None).json())       
    df_list = [pd.json_normalize(json['HourlySystemLoads']['HourlySystemLoad'], sep='_') for json in resp_list]
    final_df = pd.concat(df_list, ignore_index=True, axis=0)
    
    final_df = final_df[['BeginDate', 'Load', 'NativeLoad']]
    final_df.rename({'Load': 'actual_load_mw', 'NativeLoad': 'native_load_mw', 'BeginDate': 'load_datetime'}, axis=1, inplace=True)
    final_df = final_df.round({'actual_load_mw': 0, 'native_load_mw': 0})
    final_df = final_df.astype({'actual_load_mw': 'int16', 'native_load_mw': 'int16'})
    final_json = final_df.to_dict('records')
    DDL = """CREATE TABLE IF NOT EXISTS iso_ne_load (
        load_id SERIAL PRIMARY KEY,
        load_datetime TIMESTAMP WITH TIME ZONE,
        actual_load_mw INTEGER, 
        forecast_load_mw INTEGER,
        native_load_mw INTEGER,
        UNIQUE(load_datetime)
        );"""
    conn.run(DDL)
    print('created iso_ne_load table')
    table = 'iso_ne_load'
    for row in final_json:
        cols = ', '.join(f'"{k}"' for k in row.keys())   
        vals = ', '.join(f':{k}' for k in row.keys()) 
        stmt = f"""INSERT INTO "{table}" ({cols}) VALUES ({vals}) 
                    ON CONFLICT (load_datetime) 
                    DO UPDATE SET 
                    actual_load_mw = EXCLUDED.actual_load_mw 
                    , native_load_mw = EXCLUDED.native_load_mw ;"""
        conn.run(stmt, **row)
    print('uploaded load data')

    conn.close()

    script_name = os.path.basename(__file__)

    new_lambda_invoke_time = keys[0]['lambda_invoke_timestamp']+86401
    new_request_date_begin = pertinent_info[0]['request_date_begin']+1
    new_request_date_end = pertinent_info[0]['request_date_end']+1

    table.put_item(
        Item={
            'function_name': script_name,
            'lambda_invoke_timestamp': new_lambda_invoke_time,
            'request_date_begin': new_request_date_begin,
            'request_date_end': new_request_date_end
        }
    )

    return json.dumps({
        'response': 200,
        'script_name': script_name,
        'message': 'data successfully sent to postgres',
        'first_data_point': final_json[0],
        'last_data_point': final_json[-1],
        'new_lambda_invoke_time': new_lambda_invoke_time,
        'new_request_date_begin': new_request_date_begin,
        'new_request_date_end': new_request_date_end
        }
    )
        
def define_yyyymmdd_date_range(start, end):
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]

def extract_date_from_timestamp(timestamp, gmt_offset=-5):
    return datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=gmt_offset))).strftime('%Y-%m-%d')

def ddb_deserialize(r, type_deserializer = TypeDeserializer()):
    return type_deserializer.deserialize({"M": r})