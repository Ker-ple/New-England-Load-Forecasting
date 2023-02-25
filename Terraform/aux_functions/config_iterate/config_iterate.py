from datetime import datetime, timedelta
import json

"""
Example JSON input:
{
    "areas": ["kingston", "durham"],
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
    "areas": ["kingston", "durham"],
    "date_begin": "20230225", 
    "date_end": "20230226",
    "config": {
        "repeat": True
        "seconds_delta": 172800
    }
}
"""

def lambda_handler(event, context):

    # This function makes new dates for both iso_ne and uscrn scrapers.

    print(event)

    old_date_end = datetime.strptime(event['date_end'], '%Y%m%d')
    days_delta = event['seconds_delta']

    new_date_begin = old_date_end + time_delta(days = 1)
    new_date_end = new_date_begin + time_delta(days = days_delta)

    return {
        'date_begin': new_date_begin.strftime('%Y%m%d'),
        'date_end': new_date_end.strftime('%Y%m%d'),
        'run_mode': event['run_mode']
    }