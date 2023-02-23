import pandas as pd
import numpy as np

HEADERS = (
    'WBANNO UTC_DATE UTC_TIME LST_DATE LST_TIME CRX_VN LONGITUDE LATITUDE '
    'T_CALC T_HR_AVG T_MAX T_MIN P_CALC SOLARAD SOLARAD_FLAG SOLARAD_MAX '
    'SOLARAD_MAX_FLAG SOLARAD_MIN SOLARAD_MIN_FLAG SUR_TEMP_TYPE SUR_TEMP SUR_TEMP_FLAG SUR_TEMP_MAX SUR_TEMP_MAX_FLAG '
    'SUR_TEMP_MIN SUR_TEMP_MIN_FLAG RH_HR_AVG RH_HR_AVG_FLAG SOIL_MOISTURE_5 SOIL_MOISTURE_10 SOIL_MOISTURE_20 SOIL_MOISTURE_50 '
    'SOIL_MOISTURE_100 SOIL_TEMP_5 SOIL_TEMP_10 SOIL_TEMP_20 SOIL_TEMP_50 SOIL_TEMP_100'
)

VARIABLE_MAP = {
    'WBANNO': 'station_id',
    'LONGITUDE': 'longitude',
    'LATITUDE': 'latitude',
    'T_CALC': 'temp_air_avg_tail_5_min',
    'T_HR_AVG': 'temp_air_avg_hr',
    'T_MAX': 'temp_air_max_hr',
    'T_MIN': 'temp_air_min_hr',
    'P_CALC': 'ppt_total',
    'SOLARAD': 'ghi',
    'SR_FLAG': 'ghi_flag',
    'SOLARAD_MAX': 'ghi_max',
    'SOLARAD_MAX_FLAG': 'ghi_max_flag',
    'SOLARAD_MIN': 'ghi_min',
    'SOLARAD_MIN_FLAG': 'ghi_min_flag',
    'SUR_TEMP_TYPE': 'temp_sur_type',
    'SUR_TEMP': 'temp_sur_avg',
    'SUR_TEMP_FLAG': 'temp_sur_avg_flag',
    'SUR_TEMP_MAX': 'temp_sur_max',
    'SUR_TEMP_MAX_FLAG': 'temp_sur_max_flag',
    'SUR_TEMP_MIN': 'temp_sur_min',
    'SUR_TEMP_MIN_FLAG': 'temp_sur_min_flag',
    'RH_HR_AVG': 'rel_humidity_avg_hr',
    'RH_HR_AVG_FLAG': 'rel_humidity_avg_hr_flag',
    'WIND_1_5': 'wind_speed',
    'WIND_FLAG': 'wind_speed_flag'
}

# as specified in CRN README.txt file. excludes 1 space between columns
WIDTHS = [5, 8, 4, 8, 4, 6, 7, 7, 7, 7, 7, 7, 7, 6, 1, 6, 1, 6, 1, 1, 7, 1, 7, 1, 7, 1, 5, 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]
# add 1 to make fields contiguous (required by pandas.read_fwf)
WIDTHS = [w + 1 for w in WIDTHS]
# no space after last column
WIDTHS[-1] -= 1

# specify dtypes for potentially problematic values
DTYPES = [
    'int64', 'int64', 'int64', 'int64', 'int64', 'str', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64', 'int64', 'float64', 'int64', 'int64',
    'int64', 'float64', 'int64', 'str', 'float64', 'int64', 'float64', 'int64',
    'float64', 'int64', 'float64', 'int64', 'float64', 'float64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64', 'float64', 'float64'
]

station_id_name_dict = {
    54794: 'NH_Durham_N',
    54795: 'NH_Durham_SSW',
    54796: 'RI_Kingston_NW',
    54797: 'RI_Kingston_W'   
}

def read_uscrn(filename, start_date=None, end_date=None, **kwargs):
    default_vars_map = {
        'T_HR_AVG': 'air_temp_avg_hr',
        'P_CALC': 'ppt_total',
        'RH_HR_AVG': 'relative_humidity_avg'
        }
    variables_map = kwargs.get('variables_map', default_vars_map)

    data = pd.read_fwf(filename, header=None, names=HEADERS.split(' '),
                       widths=WIDTHS, dtype=dict(zip(HEADERS.split(' '), DTYPES)))
    # set index
    # UTC_TIME does not have leading 0s, so must zfill(4) to comply
    # with %H%M format
    dts = data[['UTC_DATE', 'UTC_TIME']].astype(str)
    dtindex = pd.to_datetime(dts['UTC_DATE'] + dts['UTC_TIME'].str.zfill(4),
                             format='%Y%m%d%H%M', utc=True)
    data = data.set_index(dtindex)
    try:
        # to_datetime(utc=True) does not work in older versions of pandas
        data = data.tz_localize('UTC')
    except TypeError:
        pass

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
    # 6. prepend each column except weather_datetime with the name of the station.

    station_name = station_id_name_dict[data.loc[0,'station_id']]
    data = data[variables_map.keys()]
    data.rename(columns=variables_map, inplace=True)
    data = data[start_date:end_date]
    data.reset_index(inplace=True)
    data.rename({'index': 'weather_datetime'}, axis=1, inplace=True)
    
    data = data.rename(columns={c: c+'_'+station_name for c in data.columns if c not in ['weather_datetime']})

    return data