import pandas as pd
import numpy as np
import math
from datetime import datetime
import os
import itertools

"""
Example JSON input:
{
    "params": {
        "date_begin": "20220811",
        "date_end": "20230224"
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
            'date_begin': '20220221', 
            'date_end': '20220308', 
            'loc_id': '4001'
        },
        {
            'date_begin': '20220309', 
            'date_end': '20220324', 
            'loc_id': '4001'
        },
        .
        .
        .,
        {
            'date_begin': '20230123', 
            'date_end': '20230206', 
            'loc_id': '4008'
        },
        {
            'date_begin': '20230207', 
            'date_end': '20230221', 
            'loc_id': '4008'
        } 
    ],
    "params": {
        "date_begin": "20220811",
        "date_end": "20230224"
    },
    "config": {
        "repeat": "True",
        "seconds_delta": "86400",
        "state_machine_arn": "arn:aws:states:us-east-1:485809471371:stateMachine:ISO"
    }
}

"""

def lambda_handler(event, context):
    print(event)

    # This function creates date ranges for the iso-ne scrapers.

    params = event['params']
    config = event['config']
    config['state_machine_arn'] = os.environ.get('STATE_MACHINE_ARN')
    loc_ids = [str(i) for i in range(4001, 4009)] 

    # This logic is complicated, so we'll take this step by step.
    # First, we get a list containing each date between our begin and and date, inclusive.
    date_range = define_yyyymmdd_date_range(event['date_begin'], event['date_end'])
    # Then, we build our list of location IDs used by ISO-NE. We avoid 4000 because we can't directly query that location.  
    loc_ids = [str(i) for i in range(4001, 4009)]
    # Then, we derive all possible combination of id and date, put each combo in a list and put those lists in a list. So, we have a list of lists.
    all_params = [[date, id] for id in loc_ids for date in date_range]
    # Then, we split that list of lists into a list of lists of lists, each index of the outer list corresponds to an ID and the lists inside that index correspond to dates.
    chunked_params = np.array_split(all_params, len(loc_ids))
    # Then, we split the innermost lists so that each inner-innermost list spans only 15 days so that each lambda has a manageable timespan to query before timeout.
    even_chunkier_params = [np.array_split(chunk, len(chunked_params[0])/15) for chunk in chunked_params]
    # Then, we format the payload by extracting the first element of the first inner-innermost list to be the start date, ... 
    # the first element of the last inner-innermost list to be the end date, and the second element of the first inner-innermost list to be the ID.
    payload = [{
        'date_begin': datetime.datetime.strptime(mini_chunk.tolist()[0][0], '%Y%m%d').strftime('%Y%m%d'), 
        'date_end': datetime.datetime.strptime(mini_chunk.tolist()[-1][0], '%Y%m%d').strftime('%Y%m%d'),
        'loc_id': mini_chunk.tolist()[0][1]}
        for chunk in even_chunkier_params for mini_chunk in chunk
    ]

    # returns first and last date of each sub-list is returned to save message space and because the invoked lambda functions can recreate the date range themselves.

    return {
        "records": payload,
        "params": params,
        "config": config
    }

def define_yyyymmdd_date_range(start, end):
    # We define a date range here because it simplifies assigning the number of lambdas.
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]

