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
    latlongs = list()
    stations = list()
    dates = list()

    for record in event['records']:
        try:
            area = record['area'].lower()
            date_begin = record['date_begin']
            date_end = record['date_end']

            lat, lon = derive_latlong(area)
            station = derive_station(area)
            dates = derive_dates(date_begin, date_end)

        except Exception:
            sys.exit("Invalid records")

        return json.dumps({
            "records": list(zip(lat, lon, station, dates))
        })

def derive_latlong(area):
    return area_latlong[area].values(), area_station[area]

def derive_station(area):
    return area_station[area]

def derive_dates(s, e):
    # This function splits an input date range into multiple smaller ranges for the uscrn scraper.

    datetime.strptime(s, '%Y%m%d')
    datetime.strptime(e, '%Y%m%d')

    new_dates = [[s,s[:4]+"1231"]] + [['%s0101'%(str(i)), '%s1231'%(str(i))] for i in range(int(s[:4])+1,int(e[:4]))]+[[e[:4] + "0101", e]]

    return json.dumps({
        'date_ranges': [
            {
                'date_begin': x[0],
                'date_end': x[-1]
            }
            for x in new_dates]
        })
        
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

area_station = {
    #"boston": [None],
    "durham": ["Durham_2_N", "Durham_2_SSW"],
    "kingston": ["Kingston_1_NW", "Kingston_1_W"]    
}