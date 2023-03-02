"""
1. Take in an area and a date range
2. Validate area
3. Validate date range
3. Derive station links and forecast coordinates
4. Derive date ranges grouped by year
"""

import os
from datetime import datetime
import numpy as np
import pandas as pd
import math

"""
Example JSON input:
{
    "params": {
        "areas": ["kingston", "durham"],
        "date_begin": "20220811",
        "date_end": "20230206"
    },
    "config": {
        "repeat": "True",
        "seconds_delta": "172800"
    }    
}
"""

"""
Example JSON output:
{
    "records": [
        {
            "station_names": ["RI_Kingston_1_NW", "RI_Kingston_1_W"],
            "date_begin": "20220811",
            "date_end": "20221108"
        },
        {
            "station_names": ["NH_Durham_2_N", "NH_Durham_2_SSW"],
            "date_begin": "20220811",
            "date_end": "20221108"
        },
        {
            "station_names": ["RI_Kingston_1_NW", "RI_Kingston_1_W"],
            "date_begin": "20221108",
            "date_end": "20220206"
        },
        .
        .
        .
    ],
    "params": {
        "areas": ["kingston", "durham"]
    },
    "config": {
        "repeat": True,
        "seconds_delta": 3600,
        "state_machine_arn": "arn:aws:states:us-east-1:485809471371:stateMachine:USCRN"
    }   
}
"""

def lambda_handler(event, context):
    payload = list()

    print(event)

    params = event['params']
    config = event['config']
    config['state_machine_arn'] = os.environ.get('STATE_MACHINE_ARN')

    date_begin = params['date_begin']
    date_end = params['date_end']

    for area in params['areas']:
        stations = derive_stations(area.lower())
        dates = derive_dates(date_begin, date_end)

        for date in dates:

            message = {
                'station_names': stations,
                'date_begin': date['date_begin'],
                'date_end': date['date_end']
            }

            payload.append(message)

    return {
        "records": payload,
        "params": params,
        "config": config
        }

def derive_stations(area):
    return area_stations[area]

# The following names are gotten from the uscrn website for the associated stations:
# e.g. https://www1.ncdc.noaa.gov/pub/data/uscrn/products/hourly02/2023/

area_stations = {
    #"boston": [None],
    "durham": ["NH_Durham_2_N", "NH_Durham_2_SSW"],
    "kingston": ["RI_Kingston_1_NW", "RI_Kingston_1_W"]    
}

def derive_dates(s, e):
    # This function creates date ranges for the iso-ne scrapers.

    dates = define_yyyymmdd_date_range(s, e)
    # a new lambda function is invoked every 30 days in consideration. Each lambda is given equal share of dates to scrape.
    num_lambdas = math.ceil(len(dates)/30)
    # returns first and last date of each sub-list is returned to save message space and because the invoked lambda functions can recreate the date range themselves.
    return [
            {
                'date_begin': datetime.strptime(x.tolist()[0], '%Y%m%d').strftime('%Y%m%d'), 
                'date_end': datetime.strptime(x.tolist()[-1], '%Y%m%d').strftime('%Y%m%d')
            }
            for x in np.array_split(dates, num_lambdas)
        ]

def define_yyyymmdd_date_range(start, end):
    # We define a date range here because it simplifies assigning the number of lambdas.
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]