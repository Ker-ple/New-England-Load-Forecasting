"""
1. Take in an area and a date range
2. Validate area
3. Validate date range
3. Derive station links and forecast coordinates
4. Derive date ranges grouped by year
"""

import json
import sys
from datetime import datetime

"""
Example JSON input:
{
    "areas": ["kingston", "durham"]
    "config": {
        "repeat": True,
        "seconds_delta": 3600
    }    
}
"""

"""
Example JSON output:
{
    "records": [
        {
            "latitude": 41.4747,
            "longitude": -71.5203,
            "area": "kingston"
        },
        {
            "latitude": 43.1339,
            "longitude": -70.9264,
            "area": "durham"
        }   
    ]
}
"""

def lambda_handler(event, context):
    payload = list()
    print(event)

    for area in event['areas']:
        area = area.lower()

        latitude, longitude = derive_latlong(area)

        message = {
            'latitude': latitude,
            'longitude': longitude,
            'area': area
        }

        payload.append(message)

    return {
        "records": payload
    }

def derive_latlong(area):
    return list(area_latlong[area].values())

area_latlong = {
    #"boston": {
    #    "latitude": "42.3601",
    #    "longitude": "71.0589"
    #},
    "durham": {
        "latitude": "43.1340",
        "longitude": "70.9264"
    },
    "kingston": {
        "latitude": "41.5568",
        "longitude": "71.4537"
    }
}
