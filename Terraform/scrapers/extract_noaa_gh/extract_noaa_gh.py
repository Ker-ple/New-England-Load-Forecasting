import pandas as pd
import pg8000.native

"""
Example JSON input:
{
    [
        {
            "area": "boston",
            "station_ids": ["72509014739"]
        },
        {   
            "area": "hartford",
            "station_ids": ["72508014740"]
        }
    ]
}
"""

"""
Example JSON output:
{
    "results": [
        "area": "boston",
        "station_ids": ["72509014739"],
        "status": "success"
    ],
    .
    .
    .
}
"""

conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

DDL = """CREATE TABLE IF NOT EXISTS weather_data (
	weather_id SERIAL PRIMARY KEY,
	weather_datetime TIMESTAMP WITH TIME ZONE,
    station_name VARCHAR,
    station_area VARCHAR,
	air_temp REAL,
    apparent_temp REAL,
	ppt_total REAL,
	relative_humidity REAL,
    wind_speed REAL,
	UNIQUE(weather_datetime, station_name)
	);"""

conn.run(DDL)

def lambda_handler(event, context):
    print(event)
    payload = list()

    for record in event:
        area, stations = zip(record['area'], record['station_ids'])
            for station in stations:
                data = get_data(station)
                cleaned_data = clean_data(data)
                cleaned_data['station_area'] = area.lower()
                data_json = cleaned_data.to_dict('records')
                print(data_json[0])
                for row in data_json:
                    cols = ', '.join(f'"{k}"' for k in row.keys())   
                    vals = ', '.join(f':{k}' for k in row.keys())
                    excluded = ', '.join(f'"EXCLUDED.{k}"' for k in row.keys())
                    stmt = f"""INSERT INTO weather_data ({cols}) VALUES ({vals});"""
                    conn.run(stmt, **row)

def get_data(station_id):
    url = url_for_station(station_id)
    data = pd.read_csv(url, header=0)
    return data

def clean_data(data_df):
    keep_cols = ['DATE', 'NAME', 'WND', 'TMP', 'DEW', 'AA1']
    variables_map = {
        'DATE': 'weather_datetime',
        'WND_SPEED': 'wind_speed',
        'AIR_TMP': 'air_temp',
        'DEW_TMP': 'dew_temp',
        'PPT_TOTAL': 'ppt_total'
    }
    new_df = data_df[keep_cols]

    #unpacked_cols = ['DATE', 'NAME', 'WND_DIR', 'WND_DIR_FLAG', 'WND_OBS_TYPE', 'WND_SPEED', 'WND_SPEED_FLAG', 'AIR_TMP', 'AIR_TMP_FLAG', 'DEW_TMP', 'DEW_FLAG', 'PPT_HOUR_SPAN', 'PPT_TOTAL', 'PPT_COND_FLAG', 'PPT_QUAL_FLAG']
    new_df[['WND_DIR', 'WND_DIR_FLAG', 'WND_OBS_TYPE', 'WND_SPEED', 'WND_SPEED_FLAG']] = pd.DataFrame(new_df['WND'].tolist(), index=new_df.index)
    new_df[['AIR_TMP', 'AIR_TMP_FLAG']] = pd.DataFrame(new_df['TMP'].tolist(), index=new_df.index)
    new_df[['DEW_TMP', 'DEW_FLAG']] = pd.DataFrame(new_df['DEW'].tolist(), index=new_df.index)
    new_df[['PPT_HOUR_SPAN', 'PPT_TOTAL', 'PPT_COND_FLAG', 'PPT_QUAL_FLAG']] = pd.DataFrame(new_df['AA1'].tolist(), index=new_df.index)

    # The following magic numbers come from page 8 of the QC specifications from the ISD data format pdf.
    new_df['WND_SPEED'] = new_df['WND_SPEED_FLAG'].where(new_df['WND_SPEED_FLAG'].isin([0, 1, 4, 5, 9]), np.nan)
    # As before, except these magic numbers come from page 11.
    new_df['AIR_TMP'] = new_df['AIR_TMP_FLAG'].where(new_df['AIR_TMP_FLAG'].isin([0, 1, 4, 5, 9, 'A', 'C', 'I', 'M', 'P', 'R', 'U']), np.nan)
    # These magic numbers come from page 11 as well.
    new_df['DEW_TMP'] = new_df['DEW_FLAG'].where(new_df['DEW_FLAG'].isin([0, 1, 4, 5, 9, 'A', 'C', 'I', 'M', 'P', 'R', 'U']), np.nan)
    # From page 14.
    new_df['PPT_TOTAL'] = new_df['PPT_QUAL_FLAG'].where(new_df['PPT_QUAL_FLAG'].isin([0, 1, 4, 5, 9, 'A', 'C', 'I', 'M', 'P', 'R', 'U']), np.nan)

    new_df = new_df[['WND_SPEED', 'AIR_TMP', 'DEW_TMP', 'PPT_TOTAL']]

def url_for_station(station_id, year):
    url = f"https://noaa-global-hourly-pds.s3.amazonaws.com/{year}/{station_id}.csv"

    return url