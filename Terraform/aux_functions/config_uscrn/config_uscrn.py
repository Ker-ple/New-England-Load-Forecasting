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

def lambda_handler(event, context):
    payload = list()

    for record in event['records']:
        area = record['area'].lower()
        date_begin = record['date_begin']
        date_end = record['date_end']

        stations = derive_stations(area)
        dates = derive_dates(date_begin, date_end)

        for date in dates:

            message = {
                'station_names': stations,
                'date_begin': date['date_begin'],
                'date_end': date['date_end']
            }

            payload.append(message)

    return json.dumps({
        "records": payload
    })

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