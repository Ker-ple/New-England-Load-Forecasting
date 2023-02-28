from datetime import datetime, timedelta, timezone
import os
import boto3
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
        "repeat": "True",
        "seconds_delta": "300"
    }
}
"""

"""
Example JSON output:
{   
    "response": {
        "executionArn": "arn:aws:states:us-east-1:485809471371:stateMachine:PIRATE",
        "startDate": datetime(2023, 2, 25)
    }
    "invoke_input": {
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
}
"""

def lambda_handler(event, context):

    # This function makes parameters for both iso_ne and uscrn scrapers, for their next run iteration.

    print(event)
`
    # to create a unique name for the next state machine iteration
    uid = datetime.now(timezone.utc).strftime('%Y%m%d-%H%H%S')
    state_machine_arn = event['state_machine_arn']
    pipeline_name = state_machine_arn.split(':')[-1]

    # getting the params and config of the current state machine execution 
    old_params = event['params']
    config = event['config']

    # making new params for the next state machine iteration
    new_params = {}

    # areas stay the same
    if "areas" in old_params:
        new_params['areas'] = old_params['areas']

    # have next iteration query starting one day after end of current query
    if "date_end" in old_params:
        old_date_end = datetime.strptime(old_params['date_end'], '%Y%m%d')
        seconds_delta = int(config['seconds_delta'])
        new_date_begin = old_date_end + timedelta(days = 1)
        new_date_end = new_date_begin + timedelta(seconds = seconds_delta)
        new_params['date_begin'] = new_date_begin.strftime('%Y%m%d')
        new_params['date_end'] = new_date_end.strftime('%Y%m%d')

    client = boto3.client('stepfunctions')
    
    response = client.start_execution(
        stateMachineArn = state_machine_arn,
        name = pipeline_name+uid,
        input = json.dumps({
            "params": new_params,
            "config": config
        })
    )

    return {
        'response': response,
        'input': {
            'params': new_params,
            'config': config
        }
    }