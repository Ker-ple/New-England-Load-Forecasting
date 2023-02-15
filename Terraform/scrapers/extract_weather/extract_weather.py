from weather_utils import *
import httpx
import pandas as pd
import json
import os
import pg8000.native
import boto3
from datetime import datetime, timezone, timedelta
from boto3.dynamodb.types import TypeDeserializer

def lambda_handler(event, context):
    print(event)

    conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

    base_url_historic_weather = os.environ.get('PIRATE_FORECAST_API')
    base_url_forecast_weather = os.environ.get('TIME_MACHINE_API')
    auth = {"Authorization": os.environ.get('WEATHER_AUTH')}

    return 0