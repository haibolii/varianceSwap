# -*- coding: utf-8 -*-

import os
import sys
import webbrowser
from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
#import dash_bootstrap_components as dbc
import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objs as go
#import pathlib
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from utils import cal_vol

#quandl_key = "TJwUr8gUrzViDvSKYi7E"
AV_KEY = "FSXSU0EGCLBCMEGI"

# get temp working directory
def resource_path(relative_path):
# get absolute path to resource
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def generate_figure(df, title):
    data = [go.Scatter(
                       x=df.index,
                       y=df[column],
                       mode="lines",
                       name=column) for column in df.columns]
    layout = dict(
            title=title,
            # width=1000,
            # height=600,
            autosize=True,
            margin={
                    "r": 30,
                    "t": 45,
                    "b": 40,
                    "l": 40,
                },
            font={"family": "Arial", "size": 12},
            showlegend=True,
            titlefont={
                "family": "Arial",
                "size": 15,
            },
            xaxis={
                "autorange": True,
                "rangeselector": {
                    "buttons": [
                        {
                            "count": 1,
                            "label": "YTD",
                            "step": "year",
                            "stepmode": "todate",
                        },
                        {
                            "count": 3,
                            "label": "3M",
                            "step": "month",
                            "stepmode": "backward",
                        },
                        {
                            "count": 6,
                            "label": "6M",
                            "step": "month",
                            "stepmode": "backward",
                        },
                        {
                            "count": 1,
                            "label": "1Y",
                            "step": "year",
                            "stepmode": "backward",
                        },
                        {
                            "count": 3,
                            "label": "3Y",
                            "step": "year",
                            "stepmode": "backward",
                        },
                        {
                            "count": 5,
                            "label": "5Y",
                            "step": "year",
                            "stepmode": "backward",
                        },
                        {
                            "label": "All",
                            "step": "all",
                        },
                    ]
                },
                "showline": True,
                "type": "date",
                "zeroline": False,
            },
            yaxis={
                "autorange": True,
                "range": [],
                "showline": True,
                "type": "linear",
                "zeroline": False,
            },
    )

    return {'data': data, 'layout': layout}

# Setup the app
app = dash.Dash(
    __name__,
    assets_folder=resource_path('assets'),
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)


app.layout = html.Div(className="body",children=[

        html.Div([html.H1("Volatility Analysis Tool"),],className="banner"),

        # left column, input parameters
        html.Div(className="three columns",children=[

                #html.Div("Left Column"),
                html.P("Input Ticker Name: "),
                dcc.Input(type="text", placeholder="Please input ticker...",
                           id="input_tkr"),
                html.P("Select Time Range: "),

                html.Div([
                         dcc.DatePickerSingle(month_format="DD MMM YYYY",
                                     display_format="DD/MM/YYYY",
                                     date=datetime(2014,1,1),
                                     initial_visible_month=datetime(2014,1,1),
                                     max_date_allowed=datetime.today()-timedelta(days=10),
                                     id="start_date",
                                     day_size=45,),
                         ],style = {"display": "inline-block"}),
                html.P("->",style = {"display": "inline-block"}),
                html.Div([
                         dcc.DatePickerSingle(month_format="DD MMM YYYY",
                                     display_format="DD/MM/YYYY",
                                     initial_visible_month=datetime.today()-timedelta(days=1),
                                     date=datetime.today()-timedelta(days=1),
                                     max_date_allowed=datetime.today()-timedelta(days=1),
                                     id="end_date",
                                     day_size=45,),
                         ],style = {"display": "inline-block"}),

                html.Button("Download Data", n_clicks=0,
                           className="button-primary",
                           id="download_button"),
                html.Div(className="tab"),
                html.Button("Generate Result", n_clicks=0,
                           className="button-primary",
                           id="display_button"),
                dcc.Loading([dcc.Store(id="raw_data"),
                             dcc.Store(id="hist_vol")]),
                dcc.ConfirmDialog(id='tkr_error', message='',),



                ]),

        # right column, output results
        html.Div(className="nine columns", children=[

                 #html.Div("Right Column"),
                 dcc.Loading(html.Div(id="result")),

                ])


    ])

@app.callback([Output("raw_data","data"), Output("hist_vol","data"), Output("tkr_error","displayed"),
               Output("tkr_error","message")],
              [Input("download_button","n_clicks")],
              [State("input_tkr","value"), State("start_date","date"), State("end_date","date")])
def pull_data(n, tkr, start, end):
    if n < 1: raise PreventUpdate
    try:
        f = web.DataReader(tkr.upper(), "av-daily", start=start, end=end, api_key=AV_KEY)
        res = f["close"].fillna(method="ffill").fillna(method="bfill")
        res.name = tkr
        vol = cal_vol(res, 30)
        return pd.DataFrame(res).to_dict(), pd.DataFrame(vol).to_dict(),False, " "
    except Exception as e:
        return None, None, True, str(e)

@app.callback(Output("result","children"),[Input("display_button","n_clicks")],
                   [State("raw_data","data"), State("hist_vol","data")])
def generate_result(n, data, vol):
    if n < 1: raise PreventUpdate
    df_data, df_vol = pd.DataFrame.from_dict(data), pd.DataFrame.from_dict(vol)
    figure_data = generate_figure(df_data, "Daily Close")
    figure_vol = generate_figure(df_vol, "Historical Vol")
    return [dcc.Graph(figure=figure_data, config={"displayModeBar": True},),
            dcc.Graph(figure=figure_vol, config={"displayModeBar": True},)]  


if __name__ == "__main__":
    import platform, socket
    app.title = "Volatility Analysis Tool"
    port = 5050
    url = "http://127.0.0.1:{}".format(port)
    
    chrome_path = {}
    # MacOS
    chrome_path['Darwin'] = r'open -a /Applications/Google\ Chrome.app %s'
    
    # Windows
    chrome_path['Windows'] = r'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

    # Linux
    chrome_path['Linux'] = r'/usr/bin/google-chrome %s'

    # check if the port is already used
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # while True:
    #     result = sock.connect_ex(('127.0.0.1', port))
    #     if result == 0:
    #         # port used
    #         port += 1
    #     else:
    #         # port not used
    #         url = "http://127.0.0.1:{}".format(port)
    #         break
    # sock.close()

    # open chrome on url
    webbrowser.get(chrome_path[platform.system()]).open(url)

    app.run_server(debug=True, port=port)
