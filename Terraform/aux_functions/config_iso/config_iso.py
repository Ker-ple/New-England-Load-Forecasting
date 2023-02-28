import pandas as pd
import numpy as np
import math
from datetime import datetime
import os

"""
Example JSON input:
{
    "params": {
        "date_begin": "20220811",
        "date_end": "20230224"
    },
    "config": {
        "repeat": "True"
        "seconds_delta": "300"
    }
}
"""

"""
Example JSON output:
{
    "records": [
        {
            "date_begin": "20220811",
            "date_end": "20221008"
        },
        .
        .
        .,
        {
            "date_begin": "20231225",
            "date_end: "20230224"
        }    
    ],
    "params": {
        "date_begin": "20220811",
        "date_end": "20230224"
    },
    "config": {
        "repeat": "True",
        "seconds_delta": "300",
        "state_machine_arn": "tresntrt"
    }
}

"""

def lambda_handler(event, context):
    print(event)

    # This function creates date ranges for the iso-ne scrapers.

    params = event['params']
    config = event['config']
    config['state_machine_arn'] = os.environ.get('STATE_MACHINE_ARN')

    dates = define_yyyymmdd_date_range(params['date_begin'], params['date_end'])
    # a new lambda function is invoked every 60 days in consideration. each lambda is given equal share of dates to scrape.
    num_lambdas = math.ceil(len(dates)/60)
    # returns first and last date of each sub-list is returned to save message space and because the invoked lambda functions can recreate the date range themselves.

    payload = [
                {
                    'date_begin': datetime.strptime(x.tolist()[0], '%Y%m%d').strftime('%Y%m%d'), 
                    'date_end': datetime.strptime(x.tolist()[-1], '%Y%m%d').strftime('%Y%m%d')
                }
                for x in np.array_split(dates, num_lambdas)
            ]

    return {
        "records": payload,
        "params": params,
        "config": config
    }

def define_yyyymmdd_date_range(start, end):
    # We define a date range here because it simplifies assigning the number of lambdas.
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]
    