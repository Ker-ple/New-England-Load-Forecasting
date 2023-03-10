"""
1. Take in an area and a date range
2. Validate area
3. Validate date range
3. Derive station links and forecast coordinates
4. Derive date ranges grouped by year
"""

import os
from datetime import datetime
import pg8000.native

"""
Example JSON input:
{
    "params": {
        "areas": "" # current behavior is to do all lats and longs in the weather_historical table by default.
    },
    "config": {
        "repeat": "True",
        "seconds_delta": "3600"
    }    
}
"""

"""
Example JSON output:
{
    "records": [
        ],
    "params": {
        "areas": ""
    }
    "config": {
        "repeat": "True",
        "seconds_delta": "3600",
        "state_machine_arn": "arn:aws:states:us-east-1:485809471371:stateMachine:PIRATE"
    }  
}
"""

def lambda_handler(event, context):
    payload = list()
    print(event)
    make_table()

    params = event['params']
    config = event['config']
    config['state_machine_arn'] = os.environ.get('STATE_MACHINE_ARN')

    return {
        "records": payload,
        "params": params,
        "config": config
    }

def make_table():
    conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    ) 

    DDL = """CREATE TABLE IF NOT EXISTS "weather_forecast" (
            "weather_forecast_id" INT NOT NULL GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            "forecasted_at" TIMESTAMP,
            "forecasted_for" TIMESTAMP,
            "apparent_temperature" REAL,
            "air_temperature" REAL,
            "relative_humidity" REAL,
            "dewpoint_temperature" REAL,
            "total_precipitation" REAL,
            "wind_speed" REAL,
            "latitude" REAL,
            "longitude" REAL,
            UNIQUE(forecasted_at, forecasted_for, latitude, longitude)
            );"""

    conn.run(DDL)
