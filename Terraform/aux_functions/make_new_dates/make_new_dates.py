from datetime import datetime, timedelta
import json

def lambda_handler(event, context):

    # This function makes new dates for both iso_ne and uscrn scrapers.

    print(event)
    event = json.loads(event)

    old_date_end = datetime.strptime(event['date_end'], '%Y%m%d')
    days_delta = event['days_delta']

    new_date_begin = old_date_end + time_delta(days = 1)
    new_date_end = new_date_begin + time_delta(days = days_delta)

    return json.dumps({
        'date_begin': new_date_begin.strftime('%Y%m%d'),
        'date_end': new_date_end.strftime('%Y%m%d'),
        'run_mode': event['run_mode']
    })