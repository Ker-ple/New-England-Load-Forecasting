import os
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pg8000

def lambda_handler(event, context):
    print(event)
    url = URL.create(
        "postgresql+pg8000",
        username=os.environ.get('DB_USERNAME'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOSTNAME'),
        database=os.environ.get('DB_NAME')
    )
    engine = create_engine(url)
    
    with engine.connect() as conn:
        past_data = get_past_data(conn)
        future_data = get_future_data(conn)
    
    regressors = [c for c in past_data.columns if c not in ['ds', 'y']]
    m = Prophet(changepoint_prior_scale=0.01, seasonality_prior_scale=1)
    m.add_country_holidays(country_name='US')
    for col in regressors:
        m.add_regressor(col)
    m.fit(past_data)
    
    predictions = m.predict(future_data)
    voi = clean_predictions(predictions)
    with engine.connect() as conn:
        put_predictions_in_db(voi, conn)
    return 'success'

def get_past_data(connection):
    dfs = list()
    area_params = []

    for params in area_params:
        values = ", ".join(str((str(lat), str(lon))) for (lat, lon) in params)
        stmt = '''SELECT 
            weather_datetime, 
            AVG(NULLIF(apparent_temperature, 'NaN')) apparent_temperature_avg, 
            AVG(NULLIF(air_temperature, 'NaN')) air_temperature_avg, 
            AVG(NULLIF(dewpoint_temperature, 'NaN')) dewpoint_temperature_avg,
            AVG(NULLIF(relative_humidity, 'NaN')) relative_humidity_avg,
            AVG(NULLIF(total_precipitation, 'NaN')) total_precipitation_avg, 
            AVG(NULLIF(wind_speed, 'NaN')) wind_speed_avg
            FROM weather_historical
            WHERE (latitude, longitude) IN ({})
            GROUP BY weather_datetime
            ORDER BY weather_datetime ASC;'''.format(values)
        df = pd.read_sql(sql=text(stmt), con=connection)
        dfs.append(df)
    stmt = '''SELECT DISTINCT 
        load_datetime
        , load_mw
        FROM grid_load
        WHERE load_datetime < now();'''
    load_historical = pd.read_sql(sql=text(stmt), con=connection)

    boston_area_weather = dfs[0].rename(columns={c:'boston_area_'+c for c in dfs[0].columns if c not in ['weather_datetime']})
    hartford_area_weather = dfs[1].rename(columns={c:'hartford_area_'+c for c in dfs[1].columns if c not in ['weather_datetime']})
    two_cluster_weather = boston_area_weather.merge(hartford_area_weather, on='weather_datetime', how='inner')
    two_cluster_weather['weather_datetime'] = two_cluster_weather['weather_datetime'].astype('datetime64')

    data = (
        two_cluster_weather
        .merge(
            load_historical, 
            left_on='weather_datetime', 
            right_on='load_datetime', 
            how='inner', indicator=True)
        .drop(columns=['_merge', 'weather_datetime'])
    )

    data['load_datetime'] = pd.to_datetime(data['load_datetime'])
    data['is_weekday'] = np.where(data['load_datetime'].dt.dayofweek >= 5, 0, 1)

    return data.rename({'load_datetime': 'ds', 'load_mw': 'y'}, axis=1)

def get_future_data(connection):
    dfs = list()
    area_params = []

    for params in area_params:
        values = ", ".join(str((str(lat), str(lon))) for (lat, lon) in params)
        stmt = '''SELECT 
            forecasted_for, 
            AVG(NULLIF(apparent_temperature, 'NaN')) apparent_temperature_avg, 
            AVG(NULLIF(air_temperature, 'NaN')) air_temperature_avg, 
            AVG(NULLIF(dewpoint_temperature, 'NaN')) dewpoint_temperature_avg,
            AVG(NULLIF(relative_humidity, 'NaN')) relative_humidity_avg,
            AVG(NULLIF(total_precipitation, 'NaN')) total_precipitation_avg, 
            AVG(NULLIF(wind_speed, 'NaN')) wind_speed_avg
            FROM weather_forecast wf
            INNER JOIN (SELECT MAX(forecasted_at) MaxDate, forecasted_for FROM weather_forecast GROUP BY forecasted_for) rec
            ON wf.forecasted_for = rec.forecasted_for AND wf.forecasted_at = rec.MaxDate
            WHERE (latitude, longitude) IN ({})
            AND forecasted_for
            GROUP BY forecasted_for
            ORDER BY forecasted_for ASC;'''.format(values)
        df = pd.read_sql(sql=text(stmt), con=connection)
        dfs.append(df)

    boston_area_weather = dfs[0].rename(columns={c:'boston_area_'+c for c in dfs[0].columns if c not in ['forecasted_for']})
    hartford_area_weather = dfs[1].rename(columns={c:'hartford_area_'+c for c in dfs[1].columns if c not in ['forecasted_for']})
    data = boston_area_weather.merge(hartford_area_weather, on='forecasted_for', how='inner')
    data['forecasted_for'] = pd.to_datetime(data['forecasted_for'])
    data['is_weekday'] = np.where(data['forecasted_for'].dt.dayofweek >= 5, 0, 1)

    return data.rename({'forecasted_for': 'ds'}, axis=1)

def clean_predictions(predictions):
    predictions = predictions[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    predictions = predictions.rename(columns={'ds': 'forecasted_for', 
                                              'yhat': 'load_mw', 
                                              'yhat_lower': 'load_mw_lower', 
                                              'yhat_upper': 'load_mw_upper'})
    predictions['forecasted_at'] = datetime.now(timezone.utc)
    return predictions.to_dict('records')

def put_predictions_in_db(predictions, connection):
    for row in predictions:
        cols = ', '.join(f'"{k}"' for k in row.keys())   
        vals = ', '.join(f':{k}' for k in row.keys())
        stmt = f"""INSERT INTO prophet_forecast ({cols}) VALUES ({vals});"""
        pd.read_sql(sql=text(stmt), con=connection)

def connect_to_db():
    

    return url