import plotly.graph_objects as go
from flask import Flask
import pandas as pd
from dash import Dash, dcc, html, Input, Output
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import os

server = Flask(__name__)
app = Dash(server=server)
app.title = 'New England Load Forecasting'

stmt = '''SELECT 
pf.forecasted_for AS datetime
, pf.load_mw AS load_mw_forecasted
, pf.load_mw_upper AS load_mw_forecasted_upper
, pf.load_mw_lower AS load_mw_forecasted_lower
, glrec.load_mw AS load_mw_actual
FROM prophet_forecast pf
INNER JOIN (SELECT MAX(forecasted_at) MaxDate, forecasted_for 
            FROM weather_forecast 
            WHERE forecasted_for >= NOW() - INTERVAL '1 DAY'
            GROUP BY forecasted_for) wfrec
ON pf.forecasted_for = wfrec.forecasted_for
AND pf.forecasted_at = wfrec.MaxDate
LEFT JOIN (SELECT load_mw, load_datetime
            FROM grid_load gl) glrec
ON pf.forecasted_for = glrec.load_datetime'''

url = URL.create(
        "postgresql+pg8000",
        username=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME')
    )

engine = create_engine(url)

with engine.connect() as conn:
    prophet_forecasts_df = pd.read_sql(sql=text(stmt), con=conn)

app.layout = html.Div([
    dcc.Graph(id="load-chart"),
    dcc.Interval(
        id='refresh',
        interval=3.6e6,
        n_intervals=0
    )
])

@app.callback(Output('load-chart', 'figure'),
              Input('refresh', 'n_intervals'))
def display_time_series(n):
    fig = go.Figure()
    fig.add_traces(
        go.Scatter(
        x=prophet_forecasts_df['datetime'],
        y=prophet_forecasts_df['load_mw_forecasted_upper'].astype(float).round(),
        mode="lines",
        name="upper bound",
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False
        )
    )
    fig.add_traces(
        go.Scatter(
            x=prophet_forecasts_df["datetime"],
            y=prophet_forecasts_df["load_mw_forecasted_lower"].astype(float).round(),
            name="lower bound",
            mode="lines",
            marker=dict(color="#444"),
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(68, 68, 68, 0.3)",
            showlegend=False
        )
    )
    fig.add_traces(
        go.Scatter(
            x=prophet_forecasts_df["datetime"],
            y=prophet_forecasts_df["load_mw_forecasted"].astype(float).round(),
            name="my forecasts",
            mode="lines",
            line=dict(color='rgb(31, 119, 180)'),
        )
    )
    fig.add_traces(
        go.Scatter(
            x=prophet_forecasts_df["datetime"],
            y=prophet_forecasts_df["load_mw_actual"].astype(float).round(),
            name="actual",
            mode="lines",
            line=dict(color="orange"),
            fill="tonexty",
            fillcolor="#eaecee",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=prophet_forecasts_df["datetime"],
            y=prophet_forecasts_df["load_mw_iso_forecasted"].astype(float).round(),
            name="iso-ne forecasts",
            mode="lines",
            line=dict(color="red"),
            fill="tonexty",
            fillcolor="#eaecee",
        )
    )
    fig.update_layout(
        yaxis_title="Load (MW)",
        title={
            "text":"Recent forecasts for the New England power grid",
            "x": .45,
            "xanchor": "center"},
        hovermode="x")
    return fig

if __name__=='__main__':
    app.run_server()