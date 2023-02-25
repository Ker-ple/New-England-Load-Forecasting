import pandas as pd
import numpy as np
import math
from datetime import datetime
import json

"""
Example JSON input:
{
    "date_begin": "20220811",
    "date_end": "20230224",
    "config": {
        "repeat": True
        "seconds_delta": 172800
    }
}
"""

"""
Example JSON output:
{
    "records": [
        {
            "date_begin": "20220811",
            "date_end": "20220909"
        },
        {
            "date_begin": "20220910",
            "date_end": "20221008"
        },
        .
        .
        .,
        {
            "date_begin": "20230126",
            "date_end: "20230224"
        }    
    ]
}

"""

def lambda_handler(event, context):
    print(event)

    # This function creates date ranges for the iso-ne scrapers.

    dates = define_yyyymmdd_date_range(event['date_begin'], event['date_end'])
    # a new lambda function is invoked every 30 dates in consideration. each lambda is given equal share of dates to scrape.
    num_lambdas = math.ceil(len(dates)/30)
    # returns first and last date of each sub-list is returned to save message space and because the invoked lambda functions can recreate the date range themselves.
    return [
            {
                'date_begin': datetime.strptime(x.tolist()[0], '%Y%m%d').strftime('%Y%m%d'), 
                'date_end': datetime.strptime(x.tolist()[-1], '%Y%m%d').strftime('%Y%m%d')
            }
            for x in np.array_split(dates, num_lambdas)]

def define_yyyymmdd_date_range(start, end):
    # We define a date range here because it simplifies assigning the number of lambdas.
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]
    