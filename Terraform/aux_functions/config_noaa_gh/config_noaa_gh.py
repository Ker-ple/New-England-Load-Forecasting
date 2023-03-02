import pandas as pd

"""
Example JSON input:
{
    "params": {
        "date_begin": "20220221",
        "date_end": "20230221",
        "areas": ["boston", "hartford"]
    },
    "config": {
        "repeat": "True",
        "seconds_delay": "86400"
    }
}
"""

"""
Example JSON output:
{
    "records": [
        {
            "area": "boston",
            "station_ids": ["72509014739"],
            "date_begin": "20220221",
            "date_end": "20230221"            
        },
        {   
            "area": "hartford",
            "station_ids": ["72508014740"]
        }
    ],
    "params": {
        "date_begin": "20220221",
        "date_end": "20230221",
        "areas": ["boston", "hartford"]
    },
    "config": {
        "repeat": "True",
        "seconds_delay": "172259200800",
        "state_machine_arn": "arn:aws:states:us-east-1:485809471371:stateMachine:NOAAGH"
    }
}
"""

def lambda_handler(event, context)
    payload = list()

    print(event)

    params = event['params']
    config = event['config']
    config['state_machine_arn'] = os.environ.get('STATE_MACHINE_ARN')    

    for area in params['areas']:
        station_ids = derive_station_ids(area.lower())

        message = {
            "area": area.lower(),
            "station_ids": station_ids
        }

        payload.append(message)
    
    return {
        "records": payload,
        "params": params, 
        "config": config
    }

def derive_station_ids(area):
    area_station_ids_dict = {
        "boston": ["72509014739"],
        "hartford": ["72508014740"]
    }

    return area_station_ids_dict[area]

def split_date(s,e):
    # Some fancy string manipulation to split a date range into contiguous ranges that don't overlap with each other and don't span multiple years.
    splits = [[s,s[:4]+"1231"]]+ [['%s0101'%(str(i)), '%s1231'%(str(i))] for i in range(int(s[:4])+1,int(e[:4]))]+[[e[:4] + "0101", e]]
    return [{
        'date_begin': split[0],
        'date_end': split[-1]
        } for split in splits
    ]    