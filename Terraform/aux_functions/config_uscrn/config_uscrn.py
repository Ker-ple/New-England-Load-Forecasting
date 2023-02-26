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
    "areas": ["kingston", "durham"],
    "date_begin": "20220811",
    "date_end": "20230224"
    "config": {
        "repeat": True,
        "seconds_delta": 86400
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
            "date_end": "20230224"
        },
        {
            "station_names": ["NH_Durham_2_N", "NH_Durham_2_SSW"],
            "date_begin": "20220811",
            "date_end": "20230224"
        }
    ]
}
"""

def lambda_handler(event, context):
    payload = list()

    date_begin = event['date_begin']
    date_end = event['date_end']

    for area in event['areas']:
        area = record['area'].lower()

        stations = derive_stations(area)
        dates = derive_dates(date_begin, date_end)

        for date in dates:

            message = {
                'station_names': stations,
                'date_begin': date['date_begin'],
                'date_end': date['date_end']
            }

            payload.append(message)

    return {
        "records": payload
        }

def derive_stations(area):
    return area_stations[area]

def derive_dates(s, e):
    # This function splits an input date range into multiple smaller ranges for the uscrn scraper.

    new_dates = [[s,s[:4]+"1231"]] + [['%s0101'%(str(i)), '%s1231'%(str(i))] for i in range(int(s[:4])+1,int(e[:4]))]+[[e[:4] + "0101", e]]

    return [            
            {
                'date_begin': x[0],
                'date_end': x[-1]
            }
            for x in new_dates]

# The following names are gotten from the uscrn website for the associated stations:
# e.g. https://www1.ncdc.noaa.gov/pub/data/uscrn/products/hourly02/2023/
area_stations = {
    #"boston": [None],
    "durham": ["NH_Durham_2_N", "NH_Durham_2_SSW"],
    "kingston": ["RI_Kingston_1_NW", "RI_Kingston_1_W"]    
}