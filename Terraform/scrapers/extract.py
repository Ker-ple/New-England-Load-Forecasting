import httpx
import pandas as pd
import json
import boto3

def lambda_handler(event, context):
    request = event

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
    final_df =  pd.concat(df_list, ignore_index=True, axis=0)

    final_df['date'] = pd.to_datetime(final_df['BeginDate']).dt.strftime('%Y-%m-%d')
    final_df['time'] = pd.to_datetime(final_df['BeginDate']).dt.strftime('%H')

    if request['request_type'] == 'forecast':
        final_df = final_df[['date', 'time', 'LoadMw', 'NetLoadMw']]
    elif request['request_type'] == 'load':
        final_df = final_df[['date', 'time', 'Load', 'NativeLoad']]

    final_json = final_df.to_dict('records')

    return final_json

    rds = boto3.client('rds')
    #table = dynamodb.Table('PowerData')

    #with table.batch_writer() as batch:
    #    for entry in final_json:
    #        batch.put_item(Item=entry)

def define_yyyymmdd_date_range(start, end):
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]