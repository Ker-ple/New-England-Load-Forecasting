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
        pf.forecasted_for AS pf_datetime
        , glrec.load_datetime AS historical_datetime
        , pf.load_mw AS load_mw_forecasted
        , pf.load_mw_upper AS load_mw_forecasted_upper
        , pf.load_mw_lower AS load_mw_forecasted_lower
        , glrec.load_mw AS load_mw_actual
        , ifrec1.load_mw AS load_mw_iso_forecasted_past
        , ifrec2.load_mw AS load_mw_iso_forecasted_future
        FROM prophet_forecast pf
        INNER JOIN (SELECT MAX(forecasted_at) MaxDate, forecasted_for
                    FROM prophet_forecast 
                    WHERE forecasted_for >= NOW() - INTERVAL '3 DAY'
                    GROUP BY forecasted_for) wfrec
        ON pf.forecasted_for = wfrec.forecasted_for
        AND pf.forecasted_at = wfrec.MaxDate
        FULL OUTER JOIN (SELECT load_mw, load_datetime
                    FROM grid_load gl
                    WHERE load_datetime >= NOW() - INTERVAL '3 DAY') glrec
        ON pf.forecasted_for = glrec.load_datetime
        LEFT JOIN (SELECT MAX(forecasted_at) MaxDate, forecasted_for, load_mw
                FROM grid_forecast
                WHERE forecasted_for >= NOW() - INTERVAL '3 DAY'
                GROUP BY forecasted_for, load_mw) ifrec1
        ON ifrec1.forecasted_for = glrec.load_datetime
        LEFT JOIN (SELECT MAX(forecasted_at) MaxDate, forecasted_for, load_mw
                FROM grid_forecast
                WHERE forecasted_for >= NOW() - INTERVAL '3 DAY'
                GROUP BY forecasted_for, load_mw) ifrec2
        ON ifrec2.forecasted_for = pf.forecasted_for
        ORDER BY pf.forecasted_for ASC;'''

url = URL.create(
        "postgresql+pg8000",
        username="kerple",
        password="k0pv7W0SrjukyN1LCGZOLzaGk",
        host="iso-project-db.cuhwc5ytptg0.us-east-1.rds.amazonaws.com",
        database="my_postgres_db"
    )

engine = create_engine(url)

with engine.connect() as conn:
    prophet_forecasts_df = pd.read_sql(sql=text(stmt), con=conn)
    prophet_forecasts_df['datetime'] = prophet_forecasts_df['pf_datetime'].fillna(prophet_forecasts_df['historical_datetime']).sort_values()
    prophet_forecasts_df['load_mw_iso_forecasted'] = prophet_forecasts_df['load_mw_iso_forecasted_past'].fillna(prophet_forecasts_df['load_mw_iso_forecasted_future']).sort_values()
    prophet_forecasts_df = prophet_forecasts_df.drop(columns=['pf_datetime', 'historical_datetime', 'load_mw_iso_forecasted_past', 'load_mw_iso_forecasted_future'])
    prophet_forecasts_df = prophet_forecasts_df.sort_values('datetime').reset_index(drop=True)

def serve_layout():
    return html.Div([
        dcc.Graph(id='load-chart'),
        dcc.Interval(
            id='refresh',
            interval=3.6e6,
            n_intervals=0
        )
    ])

app.layout = serve_layout

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
            name="my forecast",
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
        )
    )
    fig.add_traces(
        go.Scatter(
            x=prophet_forecasts_df["datetime"],
            y=prophet_forecasts_df["load_mw_iso_forecasted"].astype(float).round(),
            name="iso-ne forecast",
            mode="lines",
            line=dict(color="red"),
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
    app.run_server(debug=True, host='0.0.0.0')