import pandas as pd
import numpy as np

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
        'T_HR_AVG': 'avg_air_temp_hr',
        'P_CALC': 'ppt_total',
        'RH_HR_AVG': 'relative_humidity_avg'
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
        'WIND_1_5': 'wind_speed',
        'WIND_FLAG': 'wind_flag'
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