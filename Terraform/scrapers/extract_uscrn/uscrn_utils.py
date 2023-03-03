import pandas as pd
import numpy as np
import math

HOURLY_HEADERS = (
    'WBANNO UTC_DATE UTC_TIME LST_DATE LST_TIME CRX_VN LONGITUDE LATITUDE '
    'T_CALC T_HR_AVG T_MAX T_MIN P_CALC SOLARAD SOLARAD_FLAG SOLARAD_MAX '
    'SOLARAD_MAX_FLAG SOLARAD_MIN SOLARAD_MIN_FLAG SUR_TEMP_TYPE SUR_TEMP SUR_TEMP_FLAG SUR_TEMP_MAX SUR_TEMP_MAX_FLAG '
    'SUR_TEMP_MIN SUR_TEMP_MIN_FLAG RH_HR_AVG RH_HR_AVG_FLAG SOIL_MOISTURE_5 SOIL_MOISTURE_10 SOIL_MOISTURE_20 SOIL_MOISTURE_50 '
    'SOIL_MOISTURE_100 SOIL_TEMP_5 SOIL_TEMP_10 SOIL_TEMP_20 SOIL_TEMP_50 SOIL_TEMP_100'
)

# as specified in CRN README.txt file. excludes 1 space between columns
HOURLY_WIDTHS = [5, 8, 4, 8, 4, 6, 7, 7, 7, 7, 7, 7, 7, 6, 1, 6, 1, 6, 1, 1, 7, 1, 7, 1, 7, 1, 5, 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]
# add 1 to make fields contiguous (required by pandas.read_fwf)
HOURLY_WIDTHS = [w + 1 for w in HOURLY_WIDTHS]
# no space after last column
HOURLY_WIDTHS[-1] -= 1

# specify dtypes for potentially problematic values
HOURLY_DTYPES = [
    'int64', 'int64', 'int64', 'int64', 'int64', 'str', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64', 'int64', 'float64', 'int64', 'int64',
    'int64', 'float64', 'int64', 'str', 'float64', 'int64', 'float64', 'int64',
    'float64', 'int64', 'float64', 'int64', 'float64', 'float64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64', 'float64', 'float64'
]

station_id_name_dict = {
    54794: 'NH_Durham_2_N',
    54795: 'NH_Durham_2_SSW',
    54796: 'RI_Kingston_1_NW',
    54797: 'RI_Kingston_1_W'   
}

def read_uscrn_hourly(filename, start_date=None, end_date=None, **kwargs):
    default_vars_map = {
        'T_HR_AVG': 'air_temp',
        'P_CALC': 'ppt_total',
        'RH_HR_AVG': 'relative_humidity'
        }
    variables_map = kwargs.get('variables_map', default_vars_map)

    data = pd.read_fwf(filename, header=None, names=HOURLY_HEADERS.split(' '),
                       widths=HOURLY_WIDTHS, dtype=dict(zip(HOURLY_HEADERS.split(' '), HOURLY_DTYPES)))
    # set index
    # UTC_TIME does not have leading 0s, so must zfill(4) to comply
    # with %H%M format
    dts = data[['UTC_DATE', 'UTC_TIME']].astype(str)
    dtindex = pd.to_datetime(dts['UTC_DATE'] + dts['UTC_TIME'].str.zfill(4),
                             format='%Y%m%d%H%M', utc=True)
    data = data.set_index(dtindex)

    # Now we can set nans. This could be done a per column basis to be
    # safer, since in principle a real -99 value could occur in a -9999
    # column. Very unlikely to see that in the real world.
    for val in [-99, -999, -9999]:
        # consider replacing with .replace([-99, -999, -9999])
        data = data.where(data != val, np.nan)

    # Replacing erroneous data with nan as per USCRN specifications.
    data['RH_HR_AVG'] = data['RH_HR_AVG'].where(data['RH_HR_AVG_FLAG'] == 0, np.nan)    

    # The following lines do the following:
    # 1. get the station name.
    # 2. filter those columns, as defined in the variables_map kwarg keys.
    # 3. rename those columns, as defined in the variables map kwarg values.
    # 4. filter rows according to start and end date argument.
    # 5. add weather_datetime as a column.
    # 6. add station_name as a column.

    station_name = station_id_name_dict[data.iloc[0,0]]
    data = data[variables_map.keys()]
    data = data.rename(columns = variables_map)
    data = data[start_date:end_date]
    data = data.reset_index()
    data = data.rename(columns = {'index': 'weather_datetime'})
    data['station_name'] = station_name

    return data

SUBHOURLY_HEADERS = (
    'WBANNO UTC_DATE UTC_TIME LST_DATE LST_TIME CRX_VN LONGITUDE LATITUDE '
    'AIR_TEMPERATURE PRECIPITATION SOLAR_RADIATION SR_FLAG SURFACE_TEMPERATURE ST_TYPE ST_FLAG RELATIVE_HUMIDITY '
    'RH_FLAG SOIL_MOISTURE_5 SOIL_TEMPERATURE_5 WETNESS WET_FLAG WIND_1_5 WIND_FLAG'
)

# as specified in CRN README.txt file. excludes 1 space between columns
SUBHOURLY_WIDTHS = [5, 8, 4, 8, 4, 6, 7, 7, 7, 7, 6, 1, 7, 1, 1, 5, 1, 7, 7, 5, 1, 6, 1]
# add 1 to make fields contiguous (required by pandas.read_fwf)
SUBHOURLY_WIDTHS = [w + 1 for w in SUBHOURLY_WIDTHS]
# no space after last column
SUBHOURLY_WIDTHS[-1] -= 1

# specify dtypes for potentially problematic values
SUBHOURLY_DTYPES = [
    'int64', 'int64', 'int64', 'int64', 'int64', 'str', 'float64', 'float64',
    'float64', 'float64', 'float64', 'int64', 'float64', 'str', 'int64', 'float64',
    'int64', 'float64', 'float64', 'float64', 'int64', 'float64', 'int64'
]

def read_uscrn_subhourly(filename, start_date=None, end_date=None, **kwargs):
    default_vars_map = {
        'WIND_1_5': 'wind_speed'
        }
    variables_map = kwargs.get('variables_map', default_vars_map)

    data = pd.read_fwf(filename, header=None, names=SUBHOURLY_HEADERS.split(' '),
                       widths=SUBHOURLY_WIDTHS, dtype=dict(zip(SUBHOURLY_HEADERS.split(' '), SUBHOURLY_DTYPES)))
    # set index
    # UTC_TIME does not have leading 0s, so must zfill(4) to comply
    # with %H%M format
    dts = data[['UTC_DATE', 'UTC_TIME']].astype(str)
    dtindex = pd.to_datetime(dts['UTC_DATE'] + dts['UTC_TIME'].str.zfill(4),
                             format='%Y%m%d%H%M', utc=True)
    data = data.set_index(dtindex)

    # Now we can set nans. This could be done a per column basis to be
    # safer, since in principle a real -99 value could occur in a -9999
    # column. Very unlikely to see that in the real world.
    for val in [-99, -999, -9999]:
        # consider replacing with .replace([-99, -999, -9999])
        data = data.where(data != val, np.nan)

    # Replacing invalid wind_speed values with nans.
    data['WIND_1_5'] = data['WIND_1_5'].where(data['WIND_FLAG'] == 0, np.nan)

    # The following lines do the following:
    # 1. get the station name.
    # 2. filter those columns, as defined in the variables_map kwarg keys.
    # 3. rename those columns, as defined in the variables map kwarg values.
    # 4. filter rows according to start and end date argument.
    # 5. add weather_datetime as a column.
    # 6. add station_name as a column.

    station_name = station_id_name_dict[data.iloc[0,0]]
    data = data[variables_map.keys()]
    data = data.rename(columns=variables_map)
    data = data[start_date:end_date]
    data = data.resample('H').mean()
    data = data.reset_index()
    data = data.rename({'index': 'weather_datetime'}, axis=1)
    data['station_name'] = station_name

    return data

def url_for_station(station_name, year):
    subhourly = f"https://www1.ncdc.noaa.gov/pub/data/uscrn/products/subhourly01/{year}/CRNS0101-05-{year}-{station_name}.txt"
    hourly = f"https://www1.ncdc.noaa.gov/pub/data/uscrn/products/hourly02/{year}/CRNH0203-{year}-{station_name}.txt"

    return hourly, subhourly

def split_date(s,e):
    # Some fancy string manipulation to split a date range into contiguous ranges that don't overlap with each other and don't span multiple years.
    if s[3] != e[3]:
        splits = [[s,s[:4]+"1231"]]+ [['%s0101'%(str(i)), '%s1231'%(str(i))] for i in range(int(s[:4])+1,int(e[:4]))] +[[e[:4] + "0101", e]]

        return [{
            'date_begin': split[0],
            'date_end': split[-1]
            } for split in splits
        ]    
    else:
        return [{
            'date_begin': s,
            'date_end': e
        }]
    

def get_apparent_temp(air_temp, rel_hum, wind_speed, temp_in_C = True, rel_hum_in_pct = True, wind_speed_in_ms = True, **kwargs):
    # https://meteor.geol.iastate.edu/~ckarsten/bufkit/apparent_temperature.html
    ms_to_mph = 2.23694

    df = pd.DataFrame()

    if wind_speed_in_ms:
        wind_speed = wind_speed * ms_to_mph
    if not rel_hum_in_pct:
        rel_hum = rel_hum * 100
    if temp_in_C:
        air_temp = air_temp * 1.8 + 32

    apparent_temp = air_temp

    if air_temp > 80:
        apparent_temp = heat_index(air_temp, rel_hum)
    elif air_temp < 50:
        apparent_temp = wind_chill(air_temp, wind_speed)

    return (apparent_temp - 32) / 1.8

def heat_index(air_temp, rel_hum):
    c1 = -42.38
    c2 = 2.049
    c3 = 10.14
    c4 = -0.224
    c5 = -0.006838
    c6 = -0.05482
    c7 = 0.001228
    c8 = 0.0008528
    c9 = -0.00000199

    apparent_temp = c1 \
                    + c2 * air_temp \
                    + c3 * rel_hum \
                    + c4 * air_temp * rel_hum \
                    + c5 * air_temp * air_temp \
                    + c6 * rel_hum * rel_hum \
                    + c7 * air_temp * air_temp * rel_hum \
                    + c8 * air_temp * rel_hum * rel_hum \
                    + c9 * air_temp * air_temp * rel_hum * rel_hum

    return apparent_temp

def wind_chill(air_temp, wind_speed):
    c1 = 35.74
    c2 = .6215
    c3 = -35.75
    c4 = .4275

    apparent_temp = c1 \
                    + c2 * air_temp \
                    + c3 * math.pow(wind_speed, .16) \
                    + c4 * air_temp * math.pow(wind_speed, .16)

    return apparent_temp