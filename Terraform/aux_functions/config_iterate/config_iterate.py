from datetime import datetime, timedelta
import json

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
        "seconds_delta": "86400"
    }    
}

OR 

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
    "params": {
        "areas": ["kingston", "durham"],
        "date_begin": "20230207",
        "date_end": "20230208"
    },
    "config": {
        "repeat": True,
        "seconds_delta": "86400"
    }   
}
"""

def lambda_handler(event, context):

    # This function makes parameters for both iso_ne and uscrn scrapers, for their next run iteration.

    print(event)

    old_params = event['params']
    config = event['config']

    new_params = {}

    # areas stay the same
    if "areas" in old_params:
        new_params['areas'] = old_params['areas']

    # have next iteration query starting one day after end of current query
    if "date_end" in old_params:
        old_date_end = datetime.strptime(old_params['date_end'], '%Y%m%d')
        seconds_delta = int(config['seconds_delta'])
        new_date_begin = old_date_end + time_delta(days = 1)
        new_date_end = new_date_begin + time_delta(seconds = seconds_delta)
        new_params['date_begin'] = new_date_begin
        new_params['new_date_end'] = new_date_end  

    return {
        "params": new_params,
        "config": config
    }