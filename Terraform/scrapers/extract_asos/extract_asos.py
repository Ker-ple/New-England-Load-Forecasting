import pandas as pd
import pg8000.native
from itertools import chain
import os
import datetime
import numpy as np

"""
Example JSON input:
{  
    "date_begin": "20220221",
    "date_end": "20230221"
}
"""

"""
Example JSON output:
{
    "results": [
        {
            "state": "MA",
            "script_name": "extract_asos.py"
        },
        .
        .
        .
    ]
}
"""

conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

def lambda_handler(event, context):
    print(event)
    payload = list()
    stations_dict = {
        'MA': ['BOS','ORH','EWB','ACK','AQW','BAF','BED','BVY','CEF','CQX','FIT','FMH','GHG','HYA','LWM','MVY','ORE','OWD','PSF','PVC','PYM','TAN'],
        'ME': ['40B','8B0','AUG','BGR','BHB','CAR','FVE','GNR','HUL','IWI','IZG','LEW','MLT','NHZ','PQI','PWM','RKD','SFM','WVL'],
        'RI': ['BID','OQU','PVD','SFZ','UUU','WST'],
        'CT': ['BDL','BDR','DXR','GON','HFD','HVN','IJD','MMK','OXC','SNC'],
        'NH': ['1P1','AFN','ASH','BML','CON','DAW','EEN','HIE','LCI','LEB','MHT','MWN','PSM'],
        'VT': ['1V4','6B0','BTV','CDA','DDH','EFK','FSO','MPV','MVL','RUT','VSF']
    }

    station_ids = list(chain(*stations_dict.values()))
    data = get_data(event['date_begin'], event['date_end'], station_ids)
    cleaned_data = clean_data(data)
    data_json = cleaned_data.to_dict('records')

    print(data_json[0])
    for row in data_json:
        cols = ', '.join(f'"{k}"' for k in row.keys())   
        vals = ', '.join(f':{k}' for k in row.keys())
        stmt = f"""INSERT INTO weather_historical ({cols}) VALUES ({vals});"""
        conn.run(stmt, **row)

    return {
        "status": "success",
        "script_name": os.path.basename(__file__)
    }

def get_data(s, e, stations):
    s = datetime.datetime.strptime(s, '%Y%m%d')
    e = datetime.datetime.strptime(e, '%Y%m%d')
    noaa_url = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
    for station in stations:
        noaa_url += f"station={station}&"
    noaa_url += f"data=tmpf&data=dwpf&data=relh&data=feel&data=p01m&data=sped&year1={s.year}&month1={s.month}&day1={s.day}&year2={e.year}&month2={e.month}&day2={e.day}&tz=Etc%2FUTC&format=onlycomma&latlon=yes&elev=no&missing=null&trace=null&direct=yes&report_type=3&report_type=4"
    data = pd.read_csv(noaa_url, na_values='null', header=0)
    return data

def clean_data(raw_data):
    variables_map = {
        'station': 'station_name',
        'valid': 'weather_datetime',
        'lon': 'longitude',
        'lat': 'latitude',
        'tmpf': 'air_temperature',
        'dwpf': 'dewpoint_temperature',
        'relh': 'relative_humidity',
        'feel': 'apparent_temperature',
        'p01m': 'total_precipitation',
        'sped': 'wind_speed'
    }
    dtypes = {
        'station_name': 'str',
        'weather_datetime': 'datetime64',
        'longitude': 'float64',
        'latitude': 'float64',
        'air_temperature': 'float64',
        'dewpoint_temperature': 'float64',
        'relative_humidity': 'float64',
        'apparent_temperature': 'float64',
        'total_precipitation': 'float64',
        'wind_speed': 'float64'
    }
    # Interestingly, the following doesn't preserve the decimals properly:
    # data = (raw_data
    #        .rename(columns=variables_map)
    #        .astype(dtypes)
    #        )

    data = raw_data.rename(columns=variables_map)
    data = data.astype(dtypes)
    data['weather_datetime'] = data['weather_datetime'].dt.ceil('H')
    
    data = data.groupby(['station_name', 'weather_datetime', 'longitude', 'latitude'], as_index=False).agg(
        air_temperature=('air_temperature', np.mean),
        dewpoint_temperature=('dewpoint_temperature', np.mean),
        relative_humidity=('relative_humidity', np.mean),
        apparent_temperature=('apparent_temperature', np.mean),
        total_precipitation=('total_precipitation', np.sum),
        wind_speed=('wind_speed', np.mean)
    )
    
    cols = [col for col in data.columns if col not in ['station_name', 'weather_datetime', 'longitude', 'latitude']]
    data[cols] = data[cols].round(2)
    return data 