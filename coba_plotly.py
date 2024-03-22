import os
import csv
import json
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import paho.mqtt.client as mqtt
import plotly.graph_objs as go
from collections import deque
import random
from utils import LineCalculation, ZoneCalculation, MQTTClient, TelegramConfig
import pymongo
import pandas as pd
import dash_ag_grid as dag
from datetime import datetime
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from dash.exceptions import PreventUpdate
import time
import plotly.express as px
import dash_daq as daq
import requests
import re
#Connect To MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["MVCS"]
    collection_LINE = db["LINE"]
    collection_Params = db["Params"]
    collection_Parameter = db["Parameter"]
    connected = True
except pymongo.errors.ConnectionFailure:
    connected = False

# Initialize Dash app
app = dash.Dash(title='MVCS', update_title=None, external_stylesheets=[dbc.themes.SOLAR], suppress_callback_exceptions=True)

# Read keys directly from MongoDB collection "Parameter"
parameter_data = collection_Parameter.find_one({})
if parameter_data:
    # Exclude "_id" key from the list of keys
    keys = [key for key in parameter_data.keys() if key != "_id"]
else:
    keys = []

# The ThemeChangerAIO loads all 52  Bootstrap themed figure templates to plotly.io
theme_controls = html.Div(
    [ThemeChangerAIO(aio_id="theme")],
    className="hstack gap-3 mt-2"
)

header = html.H4(
    "Monitoring Voltage Current System", className="bg-transparent text-white p-2 mb-2 fs-1 text-center",
    style={'fontFamily': 'Rubik, sans-serif'}
)

#Dropdown1 Select Config for Graph Zone
dropdown = html.Div(
    [
        html.Label('Select Config File :', style={'color': 'white'}),
        dcc.Dropdown(
            id='config-dropdown',
            options=[{'label': doc['_id'], 'value': doc['_id']} for doc in collection_LINE.find({})],
            style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'}
        ),
    ],
    className="mb-4",
)

#Dropdown2 for select config changes parameter
dropdown2 = html.Div(
    [
        html.Label('Select Config File for Parameters :', style={'color': 'white'}),
        dcc.Dropdown(
            id='config-param-dropdown',
            options=[{'label': doc['_id'], 'value': doc['_id']} for doc in collection_Parameter.find({})],
            style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'}
        ),
    ],
    className="mb-1",
)

#Filter start input textbox
filter_start_input = dbc.Row([
    html.Label("Start Timestamp (YYYY-MM-DD_HH:MM:SS)", style={'color': 'white'}),
    html.Div(
        [
            dbc.Input(type="Timestamp", id="start-time", placeholder="Start Time", size="md", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'}),
            dbc.Label("Enter Start Time"),
        ],
    ),
],
    className="my-1"
)

#Filter end input textbox
filter_end_input = dbc.Row([
    html.Label("End Timestamp (YYYY-MM-DD_HH:MM:SS)", style={'color': 'white'}),
    html.Div([
        dbc.Input(type="Timestamp", id="end-time", placeholder="End Time", size="md", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'}),
    ]),
    dbc.Label("Enter End Time"),
],
    className="my-1",
)

#Line Parameter textbox
line_param = html.Div([dbc.Row([
            html.Label('Config Parameter', style={'color': 'white'}, className="bg-transparent p-0 mb-0 text-white fs-4 text-center"),
            html.Label("Enter RGZ data ", style={'color': 'white'}),
            dbc.Col(
                html.Div([
                    html.Div(id='last-rgz1-value', style={'color': 'white'}),
                    dbc.Input(type="Text", id="rgz1", size="sm", placeholder="RGZ1", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
                ], className="mx-1")
            ), 
            dbc.Col(
                html.Div([
                    html.Div(id='last-rgz2-value', style={'color': 'white'}),
                    dbc.Input(type="Text", id="rgz2", size="sm", placeholder="RGZ2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
                ], className="mx-1")
            ),
            dbc.Col(
                html.Div([
                    html.Div(id='last-rgz3-value', style={'color': 'white'}),
                    dbc.Input(type="Text", id="rgz3", size="sm", placeholder="RGZ3", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
                ], className="mx-1")
            )
    ],
    ),
            dbc.Row([
                    html.Label("Enter XGZ data ", style={'color': 'white'}),
                    dbc.Col(
                        html.Div([
                            html.Div(id='last-xgz1-value', style={'color': 'white'}),
                            dbc.Input(type="Text", id="xgz1", size="sm", placeholder="XGZ1", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
                        ], className="mx-1")
                    ), 
                    dbc.Col(
                        html.Div([
                            html.Div(id='last-xgz2-value', style={'color': 'white'}),
                            dbc.Input(type="Text", id="xgz2", size="sm", placeholder="XGZ2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
                        ], className="mx-1")
                    ),
                    dbc.Col(
                        html.Div([
                            html.Div(id='last-xgz3-value', style={'color': 'white'}),
                            dbc.Input(type="Text", id="xgz3", size="sm", placeholder="XGZ3", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
                        ], className="mx-1")
                    )
            ],
            ),
            dbc.Row([
                    html.Label("Enter RPZ data ", style={'color': 'white'}),
                    dbc.Col(
                        html.Div([
                            html.Div(id='last-rpz1-value', style={'color': 'white'}),
                            dbc.Input(type="Text", id="rpz1", size="sm", placeholder="RPZ1", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
                        ], className="mx-1")
                    ), 
                    dbc.Col(
                        html.Div([
                            html.Div(id='last-rpz2-value', style={'color': 'white'}),
                            dbc.Input(type="Text", id="rpz2", size="sm", placeholder="RPZ2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
                        ], className="mx-1")
                    ),
                    dbc.Col(
                        html.Div([
                            html.Div(id='last-rpz3-value', style={'color': 'white'}),
                            dbc.Input(type="Text", id="rpz3", size="sm", placeholder="RPZ3", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
                        ], className="mx-1")
                    )
            ],
            ),
dbc.Row([
        html.Label("Enter XPZ data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                html.Div(id='last-xpz1-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="xpz1", size="sm", placeholder="XPZ1", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                html.Div(id='last-xpz2-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="xpz2", size="sm", placeholder="XPZ2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                html.Div(id='last-xpz3-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="xpz3", size="sm", placeholder="XPZ3", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter Angle data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                html.Div(id='last-angle-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="angle", size="sm", placeholder="Angle", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                html.Div(id='last-z0z1_mag-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="z0z1_mag", size="sm", placeholder="z0z1_mag", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                html.Div(id='last-z0z1_ang-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="z0z1_ang", size="sm", placeholder="z0z1_ang", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter delta_t, id, line_length data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                html.Div(id='last-delta_t-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="delta_t", size="sm", placeholder="delta_t", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                html.Div(id='last-id2-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="id2", size="sm", placeholder="id2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                html.Div(id='last-line_length-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="line_length", size="sm", placeholder="line_length (KM)", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter CT RATIO data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                html.Div(id='last-CT_RATIO_HV-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="CT_RATIO_HV", size="sm", placeholder="HV", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                html.Div(id='last-CT_RATIO_LV-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="CT_RATIO_LV", size="sm", placeholder="LV", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter VT RATIO data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                html.Div(id='last-VT_RATIO_HV-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="VT_RATIO_HV", size="sm", placeholder="HV", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                html.Div(id='last-VT_RATIO_LV-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="VT_RATIO_LV", size="sm", placeholder="LV", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter CT/VT RATIO data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                html.Div(id='last-CTVT_RATIO-value', style={'color': 'white'}),
                dbc.Input(type="Text", id="CTVT_RATIO", size="sm", placeholder="CT/VT Ratio", style={ 'background-color': 'white', "border-color": "#2AA198", "border-width": "5px"})
            ], className="mx-1")
        ), 
],
),
])

#Apply Changes Button
Apply_button = html.Div(
    [
        dbc.Button("Apply Changes", id="apply-button", size="sm", color="success", className="me-1", disabled=True, n_clicks=0)
    ],
    className="d-grid gap-2 my-3",
)

# Setpoint IN textbox
setpoint = html.Div([
    dbc.Row([
        html.Label('SETPOINT IN', style={'color': 'white'}, className="bg-transparent p-0 mb-0 text-white fs-4 text-center"),
        dbc.Row([
            html.Label("Enter SET IN, NL & PL", style={'color': 'white'}),
            dbc.Col(
                html.Div([
                    html.Div(id='last-SETPOINT_IN-value', style={'color': 'white'}),
                    dbc.Input(type="Text", id="SETPOINT_IN", size="sm", placeholder="SETPOINT IN", style={ 'background-color': 'white', "border-color": "#2AA198", "border-width": "5px"})
                ], className="mx-1")
            ), 
            dbc.Col(
                html.Div([
                    html.Div(id='last-IN_NL-value', style={'color': 'white'}),
                    dbc.Input(type="Text", id="IN_NL", size="sm", placeholder="IN NL", style={ 'background-color': 'white', "border-color": "#2AA198", "border-width": "5px"})
                ], className="mx-1")
            ), 
            dbc.Col(
                html.Div([
                    html.Div(id='last-IN_PL-value', style={'color': 'white'}),
                    dbc.Input(type="Text", id="IN_PL", size="sm", placeholder="IN PL", style={ 'background-color': 'white', "border-color": "#2AA198", "border-width": "5px"})
                ], className="mx-1")
            ), 
        ]),
    ]),
])

setpoint_button = html.Div(
    [
        dbc.Button("Apply", id="setpoint-button", size="sm", color="success", className="me-1", n_clicks=0)
    ],
    className="d-grid gap-2 my-3",
)

##################################################### Filter Data ######################################################################
#Filter start input textbox
filter_start_input = dbc.Row([
    html.Label("Start Timestamp (YYYY-MM-DD_HH:MM:SS)", style={'color': 'white'}),
    html.Div(
        [
            dbc.Input(type="Timestamp", id="start-time", placeholder="Start Time", size="md", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'}),
            dbc.Label("Enter Start Time"),
        ],
    ),
],
    className="my-1"
)

#Filter end input textbox
filter_end_input = dbc.Row([
    html.Label("End Timestamp (YYYY-MM-DD_HH:MM:SS)", style={'color': 'white'}),
    html.Div([
        dbc.Input(type="Timestamp", id="end-time", placeholder="End Time", size="md", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'}),
    ]),
    dbc.Label("Enter End Time"),
],
    className="my-1",
)

#Filter Button
Filter_button = html.Div(
    [
        dbc.Button("Filter Data", id="filter-button", color="success", className="me-1", disabled=True, n_clicks=0)
    ],
    className="d-grid gap-2 my-3",
)

# Save CSV Button
csv_button = html.Div([
    html.Button("Save CSV", id="save-csv-button", className="btn btn-success me-1", disabled=True, n_clicks=0)
],
    className="d-grid gap-2 my-3",
)

filter_time = dbc.Form([filter_start_input, filter_end_input])

###################################################### Card Control ##########################################################################
#Card control1
control1 = dbc.Card(
    [dropdown, filter_time, 
     dbc.Row([
         html.Div(id="warning-message", style={'color': 'red'}),
         html.Div(id="saved-message", style={'color': 'green'}),
         dbc.Col(
            Filter_button
         ),
         dbc.Col(
            csv_button
         ),
    ]),    
     dbc.Row([
        dbc.Col(
            daq.Indicator(
                label="MongoDB Connected",
                color="#00FF00" if connected else "#90EE90",
                value=connected
                ),
            ),
        dbc.Col(
            daq.Indicator(
                label="MongoDB Disconnected",
                color="#FF0000" if not connected else "#FF6666",
                value=not connected
                ),
            )
    ])
    ],
    style={"height": 490, "width": 400},
    body=True,
)

# Card control2
control2 = dbc.Card([
    dropdown2, line_param,
    dbc.Row([
        dbc.Col(Apply_button),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id="error-message", style={'color': 'red'})),
    ]),
],
style={"height": 1000, "width": 400},
body=True,)

# Card control3
control3 = dbc.Card([
    setpoint,
    dbc.Row([
         dbc.Col(
            setpoint_button
         )
     ]
),    
],
style={"height": 200, "width": 400},
body=True)

################################################## Card voltage and current values ###########################################################
card_combined = dbc.Card(
    [
        dbc.CardBody(
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("SETPOINT_IN", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="SETPOINT_IN-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IN", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IN-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("Arus_Netral_beban_Normal", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="Arus_Netral_beban_Normal-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("Arus_Netral_beban_Puncak", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="Arus_Netral_beban_Puncak-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
            ])
        ),
        dbc.CardBody(
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("VA", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VA-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VB", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VB-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VC", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VC-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VA_Ang", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VA_Ang-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VB_Ang", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VB_Ang-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VC_Ang", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VC_Ang-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
            ])
        ),
        dbc.CardBody(
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("VAB", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VAB-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VBC", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VBC-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VCA", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VCA-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VAN", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VAN-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VBN", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VBN-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VCN", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VCN-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
            ])
        ),
        dbc.CardBody(
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("VA_3rd", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VA_3rd-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VB_3rd", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VB_3rd-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VC_3rd", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VC_3rd-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VA_5th", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VA_5th-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VB_5th", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VB_5th-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("VC_5th", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="VC_5th-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
            ])
        ),
        dbc.CardBody(
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("IA", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IA-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IB", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IB-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IC", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IC-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IA_Ang", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IA_Ang-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IB_Ang", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IB_Ang-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IC_Ang", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IC_Ang-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
            ])
        ),
        dbc.CardBody(
            dbc.Row([
               dbc.Col([
                    html.Div([
                        html.H4("IA_3rd", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IA_3rd-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IB_3rd", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IB_3rd-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IC_3rd", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IC_3rd-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IA_5th", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IA_5th-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IB_5th", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IB_5th-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]),
                dbc.Col([
                    html.Div([
                        html.H4("IC_5th", className="card-title", 
                                style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                        html.H2(id="IC_5th-value", className="card-subtitle mb-2 text-muted", 
                                style={'color': '#FFFFFF', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '14px'}),
                    ], style={'background-color': '#212529', 'padding': '10px', 'border-radius': '10px', 'text-align': 'center'})
                ]), 
            ])
        ),
    ],
)

###################################################### App Layout ########################################################################
app.layout = dbc.Container(
    [
        header,
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Nav(
                            [
                                dbc.Row([
                                            dbc.Col([
                                                control1,
                                                # ************************************
                                                # Uncomment line below when running locally!
                                                # ************************************
                                                # theme_controls
                                            ],  width=18, ),
                                            dbc.Col([
                                                control2,
                                                # ************************************
                                                # Uncomment line below when running locally!
                                                # ************************************
                                                # theme_controls
                                            ],  width=18, className="my-4"),
                                            dbc.Col([
                                                control3,
                                                # ************************************
                                                # Uncomment line below when running locally!
                                                # ************************************
                                                # theme_controls
                                            ],  width=18, className="my-4"),
                                        ]),
                            ],
                            vertical=True, pills=True
                        )
                    ],
                    width=3
                ),
                dbc.Col(
                    [
                        dbc.Row([
                                dbc.Col([
                                    card_combined,
                                ],  width=12,
                                style={'margin-bottom': '5mm','color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '24px'}
                                ),
                            ]),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Graph(id='phase-to-gnd-graph'),
                                    ],
                                    width=6,
                                    style={'margin-bottom': '5mm'}
                                ),
                                dbc.Col(
                                    [
                                        dcc.Graph(id='phase-to-phase-graph')
                                    ],
                                    width=6,
                                    style={'margin-bottom': '5mm'}
                                ),
                                
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div(id='mongo-datatable', children=[]),
                                        dcc.Interval(
                                            id='interval-component',
                                            interval=1*1000,  # in milliseconds
                                            n_intervals=0
                                        ),
                                    ],
                                    width=12
                                )
                            ]
                        )
                    ],
                    width=9
                )
            ]
        )
    ],
    fluid=True
)

######################################################### Filter DAta ######################################################################
# Callback for filtering data based on timestamps
@app.callback(
    Output('mongo-datatable', 'children'),
    Output('warning-message', 'children'),
    [Input('filter-button', 'n_clicks')],
    [State('start-time', 'value'),
     State('end-time', 'value')]
)

def filter_data(n_clicks, start_time, end_time):
    warning_message_filter = None
    if n_clicks and start_time and end_time:
        # Check if end_timestamp is earlier than start_timestamp
        if end_time < start_time:
            warning_message_filter = "End timestamp cannot be earlier than start timestamp."
            return None, warning_message_filter
        # Fetch data from MongoDB within the specified timestamp range
        filtered_data = collection_Params.find({"Timestamp": {"$gte": start_time, "$lte": end_time}})
        
        # Convert the fetched data to a DataFrame
        df = pd.DataFrame(list(filtered_data))
        df['_id'] = df['_id'].astype(str)  # Convert ObjectId to string
        
        # Display the DataFrame in a Dash DataTable
        return [
            dash_table.DataTable(
                id='our-table',
                data=df.to_dict('records'),
                columns=[{'id': p, 'name': p, 'editable': False} if p == '_id'
                         else {'id': p, 'name': p, 'editable': True}
                         for p in df.columns],
                style_table={'overflowX': 'auto', 'backgroundColor': 'rgba(255, 255, 255, 0.1)'},  # Transparan
                style_cell={'textAlign': 'left', 'fontSize': 14, 'fontFamily': 'Arial', 'padding': '5px', 'color': 'white'},  # Warna font putih
                style_header={
                    'backgroundColor': 'rgba(255, 255, 255, 0.1)',  # Transparan
                    'fontWeight': 'bold'  # Menjadikan teks header bold
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},  # Atur baris ganjil
                        'backgroundColor': 'rgba(255, 255, 255, 0.05)'  # Transparan
                    },
                    {
                        'if': {'row_index': 'even'},  # Atur baris genap
                        'backgroundColor': 'rgba(255, 255, 255, 0.1)'  # Transparan
                    },
                ],
                filter_action="native",  # Aktifkan penyaringan baris
                sort_action="native",  # Aktifkan sorting
                sort_mode="multi",  # Aktifkan sorting multi kolom
                page_size=20,
            ),
        ], warning_message_filter
    else:
        return [], warning_message_filter

@app.callback(
    Output('filter-button', 'disabled'),
    [Input('start-time', 'value'),
     Input('end-time', 'value')]
)
def update_button_disabled(start_time, end_time):
    timestamp_format = re.compile(r'^\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}$')
    if start_time is None or end_time is None:
        return True
    if not timestamp_format.match(start_time) or not timestamp_format.match(end_time):
        return True
    return False

####################################################### Save Data CSV ################################################################
@app.callback(
    Output('save-csv-button', 'n_clicks'),
    Output("saved-message", "children"),
    [Input('save-csv-button', 'n_clicks')],
    [State('start-time', 'value'),
     State('end-time', 'value')]
)
def save_csv(n_clicks, start_time, end_time):
    if n_clicks:
        if start_time and end_time:
            filtered_data = collection_Params.find({"Timestamp": {"$gte": start_time, "$lte": end_time}})
            df = pd.DataFrame(list(filtered_data))
            
            # Create folder if not exists
            folder_path = "data_csv"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            # Create CSV file with desired format
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(folder_path, f"filter_data_{timestamp}.csv")
            
            # Save DataFrame to CSV file
            df.to_csv(filename, index=False)
            return 0, "CSV file has been saved successfully."
    else:
        raise PreventUpdate

@app.callback(
    Output('save-csv-button', 'disabled'),
    [Input('mongo-datatable', 'children')]
)
def update_button_disabled(table_data):
    if table_data:
        return False
    else:
        return True
########################################################## Update Grafph ###############################################################
LINE_Mag_VI = []
LINE_Phase_Angles = []
LINE_V_Harm = []
LINE_I_Harm = []

LINE1_z0z1_mag = 6.181
LINE1_z0z1_ang = -2.55

ZA_Real = []
ZA_Imag = []
ZB_Real = []
ZB_Imag = []
ZC_Real = []
ZC_Imag = []
ZAB_Real = []
ZAB_Imag = []
ZBC_Real = []
ZBC_Imag = []
ZCA_Real = []
ZCA_Imag = []

def handle_Mag_data(data):
    LINE_Mag_VI.append(data)
    LINE_Mag_VI[:] = data

def handle_Phase_data(data):
    LINE_Phase_Angles.append(data)
    LINE_Phase_Angles[:] = data

def handle_Vharm_data(data):
    LINE_V_Harm.append(data)
    LINE_V_Harm[:] = data

def handle_Iharm_data(data):
    LINE_I_Harm.append(data)
    LINE_I_Harm[:] = data

def unpack_mag_data():
    if len(LINE_Mag_VI) == 0:
        return (0,) * 14  # Return a tuple of 14 zeros if LINE_Phase_Angles is empty
    else:
        LINE1_Freq = LINE_Mag_VI[0]
        LINE1_U1 = LINE_Mag_VI[1]
        LINE1_U2 = LINE_Mag_VI[2]
        LINE1_U3 = LINE_Mag_VI[3]
        LINE1_Uavg = LINE_Mag_VI[4]
        LINE1_U12 = LINE_Mag_VI[5]
        LINE1_U23 = LINE_Mag_VI[6]
        LINE1_U31 = LINE_Mag_VI[7]
        LINE1_ULavg = LINE_Mag_VI[8]
        LINE1_IL1 = LINE_Mag_VI[9]
        LINE1_IL2 = LINE_Mag_VI[10]
        LINE1_IL3 = LINE_Mag_VI[11]
        LINE1_ILavg = LINE_Mag_VI[12]
        LINE1_IN = LINE_Mag_VI[13]
        return LINE1_Freq, LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Uavg, LINE1_U12, LINE1_U23, LINE1_U31, LINE1_ULavg, LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_ILavg, LINE1_IN
    # return None

def unpack_phase_data():
    if len(LINE_Phase_Angles) == 0:
        return (0,) * 6  # Return a tuple of 14 zeros if LINE_Phase_Angles is empty
    else:
        LINE1_Ang_U1 = 0
        LINE1_Ang_U2 = LINE_Phase_Angles[0]
        LINE1_Ang_U3 = LINE_Phase_Angles[1]
        LINE1_Ang_I1 = LINE_Phase_Angles[2]
        LINE1_Ang_I2 = LINE_Phase_Angles[3]
        LINE1_Ang_I3 = LINE_Phase_Angles[4]
        return LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3
    # return None

def unpack_Iharm_data():
    if len(LINE_I_Harm) == 0:
        return (0,) * 6  # Return a tuple of 14 zeros if LINE_Phase_Angles is empty
    else:
        LINE1_IA3rd_Harm = LINE_I_Harm[0]
        LINE1_IA5th_Harm = LINE_I_Harm[1]
        LINE1_IB3rd_Harm = LINE_I_Harm[2]
        LINE1_IB5th_Harm = LINE_I_Harm[3]
        LINE1_IC3rd_Harm = LINE_I_Harm[4]
        LINE1_IC5th_Harm = LINE_I_Harm[5]
        
        return  LINE1_IA3rd_Harm, LINE1_IA5th_Harm, LINE1_IB3rd_Harm, LINE1_IB5th_Harm, LINE1_IC3rd_Harm, LINE1_IC5th_Harm
    # return None

def unpack_Vharm_data():
    if len(LINE_V_Harm) == 0:
        return (0,) * 6  # Return a tuple of 14 zeros if LINE_Phase_Angles is empty
    else:
        LINE1_VA3rd_Harm = LINE_V_Harm[0]
        LINE1_VA5th_Harm = LINE_V_Harm[1]
        LINE1_VB3rd_Harm = LINE_V_Harm[2]
        LINE1_VB5th_Harm = LINE_V_Harm[3]
        LINE1_VC3rd_Harm = LINE_V_Harm[4]
        LINE1_VC5th_Harm = LINE_V_Harm[5]
        
        return  LINE1_VA3rd_Harm, LINE1_VA5th_Harm, LINE1_VB3rd_Harm, LINE1_VB5th_Harm, LINE1_VC3rd_Harm, LINE1_VC5th_Harm
    # return None

def process_data():
    
    LINE1_Freq, LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Uavg, LINE1_U12, LINE1_U23, LINE1_U31, LINE1_ULavg, LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_ILavg, LINE1_IN =  unpack_mag_data()
    LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3 = unpack_phase_data()

    line_calc = LineCalculation()
    
    try :
        line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                    LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                                    LINE1_z0z1_mag, LINE1_z0z1_ang)
        LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()
        ZA_Real.append(LINE1_ZA_Real)
        ZA_Imag.append(LINE1_ZA_Imag)
        if len(ZA_Real) >= 50:
            ZA_Real.pop(0)
        if len(ZA_Imag) >= 50:
            ZA_Imag.pop(0)

        # Mendapatkan data ZB
        LINE1_ZB_Real, LINE1_ZB_Imag, LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X = line_calc.get_ZB_data()
        ZB_Real.append(LINE1_ZB_Real)
        ZB_Imag.append(LINE1_ZB_Imag)
        if len(ZB_Real) >= 50:
            ZB_Real.pop(0)
        if len(ZB_Imag) >= 50:
            ZB_Imag.pop(0)

        # Mendapatkan data ZC
        LINE1_ZC_Real, LINE1_ZC_Imag, LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X = line_calc.get_ZC_data()
        ZC_Real.append(LINE1_ZC_Real)
        ZC_Imag.append(LINE1_ZC_Imag)
        if len(ZC_Real) >= 50:
            ZC_Real.pop(0)
        if len(ZC_Imag) >= 50:
            ZC_Imag.pop(0)

        # Mendapatkan data ZAB
        LINE1_ZAB_Real, LINE1_ZAB_Imag, LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X = line_calc.get_ZAB_data()
        ZAB_Real.append(LINE1_ZAB_Real)
        ZAB_Imag.append(LINE1_ZAB_Imag)
        if len(ZAB_Real) >= 50:
            ZAB_Real.pop(0)
        if len(ZAB_Imag) >= 50:
            ZAB_Imag.pop(0)

        # Mendapatkan data ZBC
        LINE1_ZBC_Real, LINE1_ZBC_Imag, LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X = line_calc.get_ZBC_data()
        ZBC_Real.append(LINE1_ZBC_Real)
        ZBC_Imag.append(LINE1_ZBC_Imag)
        if len(ZBC_Real) >= 50:
            ZBC_Real.pop(0)
        if len(ZBC_Imag) >= 50:
            ZBC_Imag.pop(0)

        # Mendapatkan data ZCA
        LINE1_ZCA_Real, LINE1_ZCA_Imag, LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X = line_calc.get_ZCA_data()
        ZCA_Real.append(LINE1_ZCA_Real)
        ZCA_Imag.append(LINE1_ZCA_Imag)
        if len(ZCA_Real) >= 50:
            ZCA_Real.pop(0)
        if len(ZCA_Imag) >= 50:
            ZCA_Imag.pop(0)
        
        # Get real and imag  data
        IL1_Real, IL2_Real, IL3_Real, V1_Real, V2_Real, V3_Real = line_calc.get_real_data() 
        IL1_Imag, IL2_Imag, IL3_Imag, V1_Imag, V2_Imag, V3_Imag= line_calc.get_imag_data()
        IL1_Complex, IL2_Complex, IL3_Complex, V1_Complex, V2_Complex, V3_Complex = line_calc.get_complex_data()
        LINE1_IN_Real, LINE1_IN_Imag, LINE1_IN_Complex, LINE1_IN_Mag, LINE1_IN_Ang = line_calc.get_line1_IN_data()
        
        data_to_write = {
                    'Timestamp' : datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                    'DATE' : datetime.now().strftime("%Y-%m-%d"), 'TIME' : datetime.now().strftime("%H:%M:%S"),
                    'LINE_IL1' : LINE1_IL1, 'LINE_IL1-Ang' : LINE1_Ang_I1, 
                    'LINE_IL2' : LINE1_IL2, 'LINE_IL2-Ang' : LINE1_Ang_I2,
                    'LINE_IL3' : LINE1_IL3, 'LINE_IL3-Ang' : LINE1_Ang_I3,
                    'LINE_UL1' : LINE1_U1, 'LINE_UL1-Ang' : LINE1_Ang_U1,
                    'LINE_UL2' : LINE1_U2, 'LINE_UL2-Ang' : LINE1_Ang_U2,
                    'LINE_UL3' : LINE1_U3, 'LINE_UL3-Ang' : LINE1_Ang_U3,
                    'LINE_z0z1_mag' : LINE1_z0z1_mag, 'LINE_z0z1_ang':LINE1_z0z1_ang,
                    'LINE_IL1_Real' : str(IL1_Real), 'LINE_IL2_Real' : str(IL2_Real), 'LINE_IL3_Real' : str(IL3_Real),
                    'LINE_IL1_Imag' : str(IL1_Imag), 'LINE_IL2_Imag' : str(IL2_Imag), 'LINE_IL3_Imag' : str(IL3_Imag),
                    'LINE_V1_Real' : str(V1_Real), 'LINE_V2_Real' : str(V2_Real), 'LINE_V3_Real' : str(V3_Real),
                    'LINE_V1_Imag' : str(V1_Imag), 'LINE_V2_Imag' : str(V2_Imag), 'LINE_V3_Imag' : str(V3_Imag),
                    'LINE_IL1_Complex' : str(IL1_Complex), 'LINE_IL2_Complex' : str(IL2_Complex), 'LINE_IL3_Complex' : str(IL3_Complex),
                    'LINE_V1_Complex' : str(V1_Complex), 'LINE_V2_Complex' : str(V2_Complex), 'LINE_V3_Complex' : str(V3_Complex),
                    'LINE_IN_Imag' : str(LINE1_IN_Imag), 'LINE_IN_Real' : str(LINE1_IN_Real), 'LINE_IN_Mag' : str(LINE1_IN_Mag), 'LINE_IN_Ang' : str(LINE1_IN_Ang) 
                }
        # Store Data to MongoDB
        collection_Params.insert_one(data_to_write)
        time.sleep(0.2)
        
    except ZeroDivisionError:
        pass

def run_mqtt_data_retrieval():
    mqtt_client = MQTTClient(on_data_callback=handle_Mag_data)
    mqtt_client.set_mqtt_topic1("data/sensor1")  # Set MQTT topic 1
    mqtt_client.connect()


def run_mqtt_angle_retreival():
    mqtt_client = MQTTClient(on_data_callback=handle_Phase_data)
    mqtt_client.set_mqtt_topic2("data/sensor2")  # Set MQTT topic 2
    mqtt_client.connect()

def run_mqtt_Vharm_retreival():

    mqtt_client = MQTTClient(on_data_callback=handle_Vharm_data)
    mqtt_client.set_mqtt_topic2("data/sensor3")  # Set MQTT topic 3
    mqtt_client.connect()

def run_mqtt_Iharm_retreival():

    mqtt_client = MQTTClient(on_data_callback=handle_Iharm_data)
    mqtt_client.set_mqtt_topic2("data/sensor4")  # Set MQTT topic 4
    mqtt_client.connect()

# Update Graph
@app.callback(
    [Output('phase-to-gnd-graph', 'figure'),
     Output('phase-to-phase-graph', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('config-dropdown', 'value')],
    [State('phase-to-gnd-graph', 'relayoutData'),
     State('phase-to-phase-graph', 'relayoutData')])

def update_graphs(n, selected_config, relayout_data_gnd, relayout_data_phase):
    process_data()
    if not selected_config:

        return [{'data': [], 'layout': {
                   'title': 'Phase-to-Gnd',
                    'xaxis': {'title': 'Voltage'},
                    'yaxis': {'title': 'Current'},
                    'annotations': [{
                        'text': 'Please Select Config!',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                            'size': 16,
                            'color': 'red'
                        }
                    }],
                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(255, 255, 255, 0.05)',
                    'font': {'color': 'white'}
                }},
                {'data': [], 'layout': {
                    'title': 'Phase-to-Phase',
                    'xaxis': {'title': 'Voltage'},
                    'yaxis': {'title': 'Current'},
                    'annotations': [{
                        'text': 'Please Select Config!',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                            'size': 16,
                            'color': 'red'
                        }
                    }],
                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(255, 255, 255, 0.05)',
                    'font': {'color': 'white'}
                }}]

    # Ambil dokumen dari koleksi LINE berdasarkan _id yang dipilih
    config_data = collection_LINE.find_one({"_id": selected_config})
    
    # Periksa apakah dokumen ditemukan
    if not config_data:
        return {}, {}
    
    # Ambil nilai dari config_data
    phase_to_gnd_data = config_data.get('phase_to_gnd', {})
    phase_to_phase_data = config_data.get('phase_to_phase', {})

    # Ekstraksi titik-titik dari data phase-to-gnd
    config_x_phase_to_gnd = [phase_to_gnd_data[key]['x'] for key in phase_to_gnd_data]
    config_y_phase_to_gnd = [phase_to_gnd_data[key]['y'] for key in phase_to_gnd_data]

    # Ekstraksi titik-titik dari data phase-to-phase
    config_x_phase_to_phase = [phase_to_phase_data[key]['x'] for key in phase_to_phase_data]
    config_y_phase_to_phase = [phase_to_phase_data[key]['y'] for key in phase_to_phase_data]
    
    df_ZA = pd.DataFrame({'ZA_Real': ZA_Real, 'ZA_Imag': ZA_Imag})
    df_ZB = pd.DataFrame({'ZB_Real': ZB_Real, 'ZB_Imag': ZB_Imag})
    df_ZC = pd.DataFrame({'ZC_Real': ZC_Real, 'ZC_Imag': ZC_Imag})
    df_ZAB = pd.DataFrame({'ZAB_Real': ZAB_Real, 'ZAB_Imag': ZAB_Imag})
    df_ZBC = pd.DataFrame({'ZBC_Real': ZBC_Real, 'ZBC_Imag': ZBC_Imag})
    df_ZCA = pd.DataFrame({'ZCA_Real': ZCA_Real, 'ZCA_Imag': ZCA_Imag})

    # Di dalam callback function update_graphs
    df_phase_to_gnd = pd.DataFrame({
        'Voltage': config_x_phase_to_gnd,
        'Current': config_y_phase_to_gnd
    })

    # Buat plot untuk phase_to_gnd dengan Plotly Express
    fig_phase_to_gnd = px.line(df_phase_to_gnd, x='Voltage', y='Current', 
                                title='Phase-to-Gnd', color_discrete_sequence=['white'], 
                                labels={'Voltage': 'Voltage', 'Current': 'Current'},
                                markers = True)

    # Atur warna dan lebar garis
    fig_phase_to_gnd.update_traces(marker=dict(color='white', size=5),
                                    line=dict(color='#03B77A', width=5))
    

    # Plot ZA for phase to gnd graph
    za_trace = px.line(df_ZA, x="ZA_Real", y="ZA_Imag", color_discrete_sequence=['#1974D2'], markers=True)
    za_trace.update_traces(line=dict(width=5), marker=dict(size=10))
    fig_phase_to_gnd.add_trace(za_trace.data[0])
    # Plot ZB for phase to gnd graph
    zb_trace = px.line(df_ZB, x="ZB_Real", y="ZB_Imag", color_discrete_sequence=['#C724B1'], markers=True)
    zb_trace.update_traces(line=dict(width=5), marker=dict(size=10))
    fig_phase_to_gnd.add_trace(zb_trace.data[0])
    # Plot ZC for phase to gnd graph
    zc_trace = px.line(df_ZC, x="ZC_Real", y="ZC_Imag", color_discrete_sequence=['#E0E722'], markers=True)
    zc_trace.update_traces(line=dict(width=5), marker=dict(size=10))
    fig_phase_to_gnd.add_trace(zc_trace.data[0])

    # Update layout
    fig_phase_to_gnd.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.05)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'), #range=x_range),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)') #range=y_range) 
    )

    # Buat plot untuk phase_to_phase dengan Plotly Express
    df_phase_to_phase = pd.DataFrame({
        'Voltage': config_x_phase_to_phase,
        'Current': config_y_phase_to_phase
    })

    # Buat plot untuk phase_to_phase dengan Plotly Express
    fig_phase_to_phase = px.line(df_phase_to_phase, x='Voltage', y='Current', 
                                    title='Phase-to-Phase', color_discrete_sequence=['white'], 
                                    labels={'Voltage': 'Voltage', 'Current': 'Current'},
                                    markers = True)

    # Atur warna dan gaya garis
    fig_phase_to_phase.update_traces(marker=dict(color='white', size=5),
                                    line=dict(color='#03B77A', width=5))

    # Plot ZAB for phase to phase graph
    zab_trace = px.line(df_ZAB, x="ZAB_Real", y="ZAB_Imag", color_discrete_sequence=['#FFAD00'], markers=True)
    zab_trace.update_traces(line=dict(width=5), marker=dict(size=10))
    fig_phase_to_phase.add_trace(zab_trace.data[0])
    # Plot ZAB for phase to phase graph
    zbc_trace = px.line(df_ZBC, x="ZBC_Real", y="ZBC_Imag", color_discrete_sequence=['#D22730'], markers=True)
    zbc_trace.update_traces(line=dict(width=5), marker=dict(size=10))
    fig_phase_to_phase.add_trace(zbc_trace.data[0])
    # Plot ZAB for phase to phase graph
    zca_trace = px.line(df_ZCA, x="ZCA_Real", y="ZCA_Imag", color_discrete_sequence=['#AFFC41'], markers=True)
    zca_trace.update_traces(line=dict(width=5), marker=dict(size=10))
    fig_phase_to_phase.add_trace(zca_trace.data[0])
            
    # Update layout
    fig_phase_to_phase.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.05)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'), #range=x_range),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)') #range=y_range)
    )
    
    # Memeriksa apakah ada perubahan zoom pada plot phase-to-gnd
    if relayout_data_gnd:
        zoom_info_gnd = relayout_data_gnd

        # Memeriksa apakah zoom in atau zoom out pada plot phase-to-gnd
        if 'xaxis.range[0]' in zoom_info_gnd:
            fig_phase_to_gnd.update_xaxes(range=[zoom_info_gnd['xaxis.range[0]'], zoom_info_gnd['xaxis.range[1]']])
        if 'yaxis.range[0]' in zoom_info_gnd:
            fig_phase_to_gnd.update_yaxes(range=[zoom_info_gnd['yaxis.range[0]'], zoom_info_gnd['yaxis.range[1]']])

    # Memeriksa apakah ada perubahan zoom pada plot phase-to-phase
    if relayout_data_phase:
        zoom_info_phase = relayout_data_phase

        # Memeriksa apakah zoom in atau zoom out pada plot phase-to-phase
        if 'xaxis.range[0]' in zoom_info_phase:
            fig_phase_to_phase.update_xaxes(range=[zoom_info_phase['xaxis.range[0]'], zoom_info_phase['xaxis.range[1]']])
        if 'yaxis.range[0]' in zoom_info_phase:
            fig_phase_to_phase.update_yaxes(range=[zoom_info_phase['yaxis.range[0]'], zoom_info_phase['yaxis.range[1]']])

    return fig_phase_to_gnd, fig_phase_to_phase

########################################################## Update Parameter ###################################################################
# Callback to update parameter values in MongoDB
@app.callback(
    Output('rgz1', 'value'),
    Output('rgz2', 'value'),
    Output('rgz3', 'value'),
    Output('xgz1', 'value'),
    Output('xgz2', 'value'),
    Output('xgz3', 'value'),
    Output('rpz1', 'value'),
    Output('rpz2', 'value'),
    Output('rpz3', 'value'),
    Output('xpz1', 'value'),
    Output('xpz2', 'value'),
    Output('xpz3', 'value'),
    Output('angle', 'value'),
    Output('z0z1_mag', 'value'),
    Output('z0z1_ang', 'value'),
    Output('delta_t', 'value'),
    Output('id2', 'value'),
    Output('line_length', 'value'),
    Output('CT_RATIO_HV', 'value'),
    Output('CT_RATIO_LV', 'value'),
    Output('VT_RATIO_HV', 'value'),
    Output('VT_RATIO_LV', 'value'),
    Output('CTVT_RATIO', 'value'),
    Output('error-message', 'children'),
    Input('apply-button', 'n_clicks'),
    [
        State('rgz1', 'value'), 
        State('rgz2', 'value'), 
        State('rgz3', 'value'), 
        State('xgz1', 'value'), 
        State('xgz2', 'value'), 
        State('xgz3', 'value'), 
        State('rpz1', 'value'), 
        State('rpz2', 'value'), 
        State('rpz3', 'value'), 
        State('xpz1', 'value'), 
        State('xpz2', 'value'), 
        State('xpz3', 'value'), 
        State('angle', 'value'), 
        State('z0z1_mag', 'value'), 
        State('z0z1_ang', 'value'), 
        State('delta_t', 'value'), 
        State('id2', 'value'), 
        State('line_length', 'value'), 
        State('CT_RATIO_HV', 'value'), 
        State('CT_RATIO_LV', 'value'), 
        State('VT_RATIO_HV', 'value'), 
        State('VT_RATIO_LV', 'value'), 
        State('CTVT_RATIO', 'value'),
        State('config-param-dropdown', 'value')
    ]
)

def update_parameter(n_clicks, rgz1, rgz2, rgz3, xgz1, xgz2, xgz3, rpz1, rpz2, rpz3, xpz1, xpz2, xpz3, angle, z0z1_mag, z0z1_ang, delta_t, id2, line_length, CT_RATIO_HV, CT_RATIO_LV, VT_RATIO_HV, VT_RATIO_LV, CTVT_RATIO, selected_config):
    messages = None
    if n_clicks is not None and n_clicks > 0:
        # Mengonversi nilai menjadi float jika tidak kosong
        try:
            float_values = [float(val) if val else None for val in [rgz1, rgz2, rgz3, xgz1, xgz2, xgz3, rpz1, rpz2, rpz3, xpz1, xpz2, xpz3, angle, z0z1_mag, z0z1_ang, delta_t, id2, line_length, CT_RATIO_HV, CT_RATIO_LV, VT_RATIO_HV, VT_RATIO_LV, CTVT_RATIO]]
        except ValueError:
            messages = "Please enter numerical values only."
            return (None,) * 23 + (messages,)
        
        if all(value is not None for value in float_values) and selected_config:
            parameter_id = selected_config  
            # Update parameter values directly into Parameter collection
            collection_Parameter.update_one({'_id': parameter_id}, {'$set': {'rgz1': float_values[0], 'rgz2': float_values[1], 'rgz3': float_values[2], 'xgz1': float_values[3], 'xgz2': float_values[4], 'xgz3': float_values[5], 'rpz1': float_values[6], 'rpz2': float_values[7], 'rpz3': float_values[8], 'xpz1': float_values[9], 'xpz2': float_values[10], 'xpz3': float_values[11], 'angle': float_values[12], 'z0z1_mag': float_values[13], 'z0z1_ang': float_values[14], 'delta_t': float_values[15], 'id2': float_values[16], 'line_length': float_values[17], 'CT_RATIO_HV': float_values[18], 'CT_RATIO_LV': float_values[19], 'VT_RATIO_HV': float_values[20], 'VT_RATIO_LV': float_values[21], 'CTVT_RATIO': float_values[22]}})
            
            if selected_config:
                filter_query = {"_id": selected_config}
                # Lakukan perhitungan berdasarkan nilai dari collection_Parameter yang diperbarui
                result = collection_Parameter.find_one(filter_query)

                if result:
                    LINE1_xpz1 = result.get('xpz1')
                    LINE1_xpz2 = result.get('xpz2')
                    LINE1_xpz3 = result.get('xpz3')
                    LINE1_rpz1 = result.get('rpz1')
                    LINE1_rpz2 = result.get('rpz2')
                    LINE1_rpz3 = result.get('rpz3')
                    LINE1_xgz1 = result.get('xgz1')
                    LINE1_xgz2 = result.get('xgz2')
                    LINE1_xgz3 = result.get('xgz3')
                    LINE1_rgz1 = result.get('rgz1')
                    LINE1_rgz2 = result.get('rgz2')
                    LINE1_rgz3 = result.get('rgz3')
                    LINE1_angle = result.get('angle')
                    LINE1_z0z1_mag = result.get('z0z1_mag')
                    LINE1_z0z1_ang = result.get('z0z1_ang')
                    zone_calc = ZoneCalculation()

                    zone_calc.calculate_values(LINE1_xpz1, LINE1_xpz2, LINE1_xpz3, LINE1_rpz1, LINE1_rpz2, LINE1_rpz3,
                                        LINE1_xgz1, LINE1_xgz2, LINE1_xgz3, LINE1_rgz1, LINE1_rgz2, LINE1_rgz3, LINE1_angle, LINE1_z0z1_mag,
                                        LINE1_z0z1_ang)

                    ################################# PHASE TO GROUND ################################################
                    # Getting the real and imaginary data
                    LINE1_Z1_PG_Real, LINE1_Z2_PG_Real, LINE1_Z3_PG_Real =  zone_calc.get_PG_real_data()
                    pg_LINE1_reach_z1_x, pg_LINE1_reach_z2_x, pg_LINE1_reach_z3_x = LINE1_Z1_PG_Real, LINE1_Z2_PG_Real, LINE1_Z3_PG_Real

                    LINE1_Z1_PG_Imag, LINE1_Z2_PG_Imag, LINE1_Z3_PG_Imag = zone_calc.get_PG_imag_data()
                    pg_LINE1_reach_z1_y, pg_LINE1_reach_z2_y, pg_LINE1_reach_z3_y = LINE1_Z1_PG_Imag, LINE1_Z2_PG_Imag, LINE1_Z3_PG_Imag

                    pg_top_right_z1_x, pg_top_right_z2_x, pg_top_right_z3_x =  zone_calc.get_tr_pg_x()

                    pg_top_right_z1_y= pg_LINE1_reach_z1_y
                    pg_top_right_z2_y= pg_LINE1_reach_z2_y
                    pg_top_right_z3_y= pg_LINE1_reach_z3_y

                    pg_top_left_z1_x= LINE1_Z1_PG_Real-(0.5*LINE1_rgz1)
                    pg_top_left_z1_y= pg_LINE1_reach_z1_y
                    pg_top_left_z2_x= LINE1_Z2_PG_Real-(0.5*LINE1_rgz2)
                    pg_top_left_z2_y= pg_LINE1_reach_z2_y
                    pg_top_left_z3_x= LINE1_Z3_PG_Real-(0.5*LINE1_rgz3)
                    pg_top_left_z3_y= pg_LINE1_reach_z3_y



                    pg_down_right_z1_x, pg_down_right_z2_x, pg_down_right_z3_x = zone_calc.get_dr_pg_x()
                    pg_down_right_z1_y, pg_down_right_z2_y, pg_down_right_z3_y = zone_calc.get_dr_pg_y()


                    pg_down_left_z1_x= -0.5 * pg_down_right_z1_x
                    pg_down_left_z1_y= 0.5 * abs(pg_down_right_z1_y)
                    pg_down_left_z2_x= -0.5 * pg_down_right_z2_x
                    pg_down_left_z2_y= 0.5 * abs(pg_down_right_z2_y)
                    pg_down_left_z3_x= -0.5 * pg_down_right_z3_x
                    pg_down_left_z3_y= 0.5 * abs(pg_down_right_z2_y)

                    pg_right_side_z1_x= pg_top_right_z1_x
                    pg_right_side_z1_y= pg_LINE1_reach_z1_y
                    pg_right_side_z2_x= pg_top_right_z2_x
                    pg_right_side_z2_y= pg_LINE1_reach_z2_y
                    pg_right_side_z3_x= pg_top_right_z3_x
                    pg_right_side_z3_y= pg_LINE1_reach_z3_y

                    pg_left_side_z1_x= pg_down_left_z1_x
                    pg_left_side_z1_y= pg_down_left_z1_y
                    pg_left_side_z2_x= pg_down_left_z2_x
                    pg_left_side_z2_y= pg_down_left_z1_y
                    pg_left_side_z3_x= pg_down_left_z3_x
                    pg_left_side_z3_y= pg_down_left_z1_y

                    ################################# PHASE TO PHASE ################################################

                    # Getting the real and imaginary data
                    LINE1_Z1_PP_Real, LINE1_Z2_PP_Real, LINE1_Z3_PP_Real =  zone_calc.get_PP_real_data()
                    pp_LINE1_reach_z1_x, pp_LINE1_reach_z2_x, pp_LINE1_reach_z3_x = LINE1_Z1_PP_Real, LINE1_Z2_PP_Real, LINE1_Z3_PP_Real

                    LINE1_Z1_PP_Imag, LINE1_Z2_PP_Imag, LINE1_Z3_PP_Imag = zone_calc.get_PP_imag_data()
                    pp_LINE1_reach_z1_y, pp_LINE1_reach_z2_y, pp_LINE1_reach_z3_y = LINE1_Z1_PP_Imag, LINE1_Z2_PP_Imag, LINE1_Z3_PP_Imag

                    pp_top_right_z1_x, pp_top_right_z2_x, pp_top_right_z3_x =  zone_calc.get_tr_pp_x()


                    pp_top_right_z1_y= pp_LINE1_reach_z1_y
                    pp_top_right_z2_y= pp_LINE1_reach_z2_y
                    pp_top_right_z3_y= pp_LINE1_reach_z3_y

                    pp_top_left_z1_x= LINE1_Z1_PP_Real-(0.5*LINE1_rpz1)
                    pp_top_left_z1_y= pp_LINE1_reach_z1_y
                    pp_top_left_z2_x= LINE1_Z2_PP_Real-(0.5*LINE1_rpz2)
                    pp_top_left_z2_y= pp_LINE1_reach_z2_y
                    pp_top_left_z3_x= LINE1_Z3_PP_Real-(0.5*LINE1_rpz3)
                    pp_top_left_z3_y= pp_LINE1_reach_z3_y

                    pp_down_right_z1_x, pp_down_right_z2_x, pp_down_right_z3_x = zone_calc.get_dr_pp_x()
                    pp_down_right_z1_y, pp_down_right_z2_y, pp_down_right_z3_y = zone_calc.get_dr_pp_y()

                    pp_down_left_z1_x= -0.5 * pp_down_right_z1_x
                    pp_down_left_z1_y= 0.5 * abs(pp_down_right_z1_y)
                    pp_down_left_z2_x= -0.5 * pp_down_right_z2_x
                    pp_down_left_z2_y= 0.5 * abs(pp_down_right_z2_y)
                    pp_down_left_z3_x= -0.5 * pp_down_right_z3_x
                    pp_down_left_z3_y= 0.5 * abs(pp_down_right_z3_y)

                    pp_right_side_z1_x= pp_top_right_z1_x
                    pp_right_side_z1_y= pp_LINE1_reach_z1_y
                    pp_right_side_z2_x= pp_top_right_z2_x
                    pp_right_side_z2_y= pp_LINE1_reach_z2_y
                    pp_right_side_z3_x= pp_top_right_z3_x
                    pp_right_side_z3_y= pp_LINE1_reach_z3_y

                    pp_left_side_z1_x= pp_down_left_z1_x
                    pp_left_side_z1_y= pp_down_left_z1_y
                    pp_left_side_z2_x= pp_down_left_z2_x
                    pp_left_side_z2_y= pp_down_left_z1_y
                    pp_left_side_z3_x= pp_down_left_z3_x
                    pp_left_side_z3_y= pp_down_left_z1_y


                    # Simpan hasil perhitungan ke dalam dokumen collection_LINE
                    line_data = {
                        "_id": parameter_id,
                        "phase_to_gnd": {
                            "point": {"x": 0, "y": 0},
                            "reach_z1": {"x": pg_LINE1_reach_z1_x, "y": pg_LINE1_reach_z1_y},
                            "reach_z2": {"x": pg_LINE1_reach_z2_x, "y": pg_LINE1_reach_z2_y},
                            "reach_z3": {"x": pg_LINE1_reach_z3_x, "y": pg_LINE1_reach_z3_y},
                            "kanan_atas_z3": {"x": pg_top_right_z3_x, "y": pg_top_right_z3_y},
                            "kanan_atas_z2": {"x": pg_top_right_z2_x, "y": pg_top_right_z2_y},
                            "kanan_atas_z1": {"x": pg_top_right_z1_x, "y": pg_top_right_z1_y},
                            "kanan_bawah_z1": {"x": pg_down_right_z1_x, "y": pg_down_right_z1_y},
                            "kiri_bawah_z1": {"x": pg_down_left_z1_x, "y": pg_down_left_z1_y},
                            "kiri_atas_z1": {"x": pg_top_left_z1_x, "y": pg_top_left_z1_y},
                            "kiri_atas_z2": {"x": pg_top_left_z2_x, "y": pg_top_left_z2_y},
                            "kiri_atas_z3": {"x": pg_top_left_z3_x, "y": pg_top_left_z3_y},
                            "kanan_samping_z3": {"x": pg_right_side_z3_x, "y": pg_right_side_z3_y},
                            "kanan_samping_z2": {"x": pg_right_side_z2_x, "y": pg_right_side_z2_y},
                            "kiri_samping_z2": {"x": pg_left_side_z2_x, "y": pg_left_side_z2_y},
                            "kiri_samping_z1": {"x": pg_left_side_z1_x, "y": pg_left_side_z1_y},
                            "kanan_samping_z1": {"x": pg_right_side_z1_x, "y": pg_right_side_z1_y},
                            "kanan_bawah_z2": {"x": pg_down_right_z2_x, "y": pg_down_right_z2_y},
                            "kiri_bawah_z2": {"x": pg_down_left_z2_x, "y": pg_down_left_z2_y},
                            "kiri_samping_z3": {"x": pg_left_side_z3_x, "y": pg_left_side_z3_y},
                            "kiri_bawah_z3": {"x": pg_down_left_z3_x, "y": pg_down_left_z3_y},
                            "kanan_bawah_z3": {"x": pg_down_right_z3_x, "y": pg_down_right_z3_y}
                        },
                        "phase_to_phase": {
                            "kiri_samping_z3": {"x": pp_left_side_z3_x, "y": pp_left_side_z3_y},
                            "kanan_bawah_z3_2": {"x": pp_down_right_z3_x, "y": pp_down_right_z3_y},
                            "kanan_atas_z3_2": {"x": pp_top_right_z3_x, "y": pp_top_right_z3_y},
                            "kiri_atas_z3_2": {"x": pp_top_left_z3_x, "y": pp_top_left_z3_y},
                            "kiri_bawah_z3_2": {"x": pp_down_left_z3_x, "y": pp_down_left_z3_y},
                            "kiri_bawah_z2": {"x": pp_down_left_z2_x, "y": pp_down_left_z2_y},
                            "kiri_samping_z2": {"x": pp_left_side_z2_x, "y": pp_left_side_z2_y},
                            "kiri_atas_z2": {"x": pp_top_left_z2_x, "y": pp_top_left_z2_y},
                            "kanan_atas_z2_2": {"x": pp_top_right_z2_x, "y": pp_top_right_z2_y},
                            "kanan_samping_z2_2": {"x": pp_right_side_z2_x, "y": pp_right_side_z2_y},
                            "kanan_bawah_z2_2": {"x": pp_down_right_z2_x, "y": pp_down_right_z2_y},
                            "kanan_bawah_z1": {"x": pp_down_right_z1_x, "y": pp_down_right_z1_y},
                            "kanan_samping_z1": {"x": pp_right_side_z1_x, "y": pp_right_side_z1_y},
                            "kanan_atas_z1": {"x": pp_top_right_z1_x, "y": pp_top_right_z1_y},
                            "start_point": {"x": 0, "y": 0},
                            "kiri_atas_z1_2": {"x": pp_top_left_z1_x, "y": pp_top_left_z1_y},
                            "kiri_samping_z1_2": {"x": pp_left_side_z1_x, "y": pp_left_side_z1_y},
                            "kiri_bawah_z1_2": {"x": pp_down_left_z1_x, "y": pp_down_left_z1_y},
                            "reach_z1": {"x": pp_LINE1_reach_z1_x, "y": pp_LINE1_reach_z1_y},
                            "reach_z2": {"x": pp_LINE1_reach_z2_x, "y": pp_LINE1_reach_z2_y},
                            "reach_z3": {"x": pp_LINE1_reach_z3_x, "y": pp_LINE1_reach_z3_y},
                            "kanan_samping_z3_2": {"x": pp_right_side_z3_x, "y": pp_right_side_z3_y}
                        }
                    }

                    collection_LINE.update_one({'_id': parameter_id}, {'$set': line_data}, upsert=True)

                    return tuple(float_values) + (messages,)
    return (None,) * 23 + (messages,)

@app.callback(
    Output('apply-button', 'disabled'),  # Menggunakan output untuk menonaktifkan tombol apply
    [Input('rgz1', 'value'),
     Input('rgz2', 'value'),
     Input('rgz3', 'value'),
     Input('xgz1', 'value'),
     Input('xgz2', 'value'),
     Input('xgz3', 'value'),
     Input('rpz1', 'value'),
     Input('rpz2', 'value'),
     Input('rpz3', 'value'),
     Input('xpz1', 'value'),
     Input('xpz2', 'value'),
     Input('xpz3', 'value'),
     Input('angle', 'value'),
     Input('z0z1_mag', 'value'),
     Input('z0z1_ang', 'value'),
     Input('delta_t', 'value'),
     Input('id2', 'value'),
     Input('line_length', 'value'),
     Input('CT_RATIO_HV', 'value'),
     Input('CT_RATIO_LV', 'value'),
     Input('VT_RATIO_HV', 'value'),
     Input('VT_RATIO_LV', 'value'),
     Input('CTVT_RATIO', 'value')]
)
def disable_apply_button(*args):
    # Memeriksa apakah ada kotak parameter yang belum terisi
    if any(arg is None or arg == '' for arg in args):
        return True  # Menonaktifkan tombol jika ada parameter yang kosong
    else:
        return False

@app.callback(
    [Output('last-rgz1-value', 'children'),
     Output('last-rgz2-value', 'children'),
     Output('last-rgz3-value', 'children'),
     Output('last-xgz1-value', 'children'),
     Output('last-xgz2-value', 'children'),
     Output('last-xgz3-value', 'children'),
     Output('last-rpz1-value', 'children'),
     Output('last-rpz2-value', 'children'),
     Output('last-rpz3-value', 'children'),
     Output('last-xpz1-value', 'children'),
     Output('last-xpz2-value', 'children'),
     Output('last-xpz3-value', 'children'),
     Output('last-angle-value', 'children'),
     Output('last-z0z1_mag-value', 'children'),
     Output('last-z0z1_ang-value', 'children'),
     Output('last-delta_t-value', 'children'),
     Output('last-id2-value', 'children'),
     Output('last-line_length-value', 'children'),
     Output('last-CT_RATIO_HV-value', 'children'),
     Output('last-CT_RATIO_LV-value', 'children'),
     Output('last-VT_RATIO_HV-value', 'children'),
     Output('last-VT_RATIO_LV-value', 'children'),
     Output('last-CTVT_RATIO-value', 'children'),],
    [Input('config-param-dropdown', 'value')]  
)
def update_last_values(selected_config):
    if selected_config:
        parameter = collection_Parameter.find_one({'_id': selected_config})
        if parameter:
            values = []
            for param in ['rgz1', 'rgz2', 'rgz3', 'xgz1', 'xgz2', 'xgz3', 'rpz1', 'rpz2', 'rpz3', 'xpz1', 'xpz2', 'xpz3', 'angle', 'z0z1_mag', 'z0z1_ang', 'delta_t', 'id2', 'line_length', 'CT_RATIO_HV', 'CT_RATIO_LV', 'VT_RATIO_HV', 'VT_RATIO_LV', 'CTVT_RATIO']:
                if param in parameter:
                    values.append(html.Div(f'Last: {parameter[param]}', style={'color': 'white'}))
            return values
    # Jika tidak ada config yang dipilih atau tidak ada data untuk config yang dipilih, kembalikan list kosong
    return [''] * 23

#################################################### Voltage and Current Values ##############################################################################################################################################################################################################################################################################################################################################################
SETPOINT_IN = None
IN_NL = None
IN_PL = None
config = TelegramConfig("@Mvcslog", "bot7172672222:AAFqGCbZgQC-ch4KXl7NhfBkTS8OoGq-35E", 150)

def get_voltage_current():
    LINE1_Freq, LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Uavg, LINE1_U12, LINE1_U23, LINE1_U31, LINE1_ULavg, LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_ILavg, LINE1_IN =  unpack_mag_data()
    LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3 = unpack_phase_data()
    LINE1_IA3rd_Harm, LINE1_IA5th_Harm, LINE1_IB3rd_Harm, LINE1_IB5th_Harm, LINE1_IC3rd_Harm, LINE1_IC5th_Harm = unpack_Iharm_data()
    LINE1_VA3rd_Harm, LINE1_VA5th_Harm, LINE1_VB3rd_Harm, LINE1_VB5th_Harm, LINE1_VC3rd_Harm, LINE1_VC5th_Harm = unpack_Vharm_data()
    IN = round(random.uniform(-1, 10), 2)

    IA = LINE1_IL1 
    IA_Ang = LINE1_Ang_I1
    IB = LINE1_IL2 
    IB_Ang = LINE1_Ang_I2
    IC = LINE1_IL3 
    IC_Ang = LINE1_Ang_I3

    VA = LINE1_U1 
    VA_Ang = LINE1_Ang_U1
    VB = LINE1_U2 
    VB_Ang = LINE1_Ang_U2
    VC = LINE1_U3 
    VC_Ang =LINE1_Ang_U3

    VAB = LINE1_U12 
    VBC = LINE1_U12 
    VCA = LINE1_U12 

    VAN = LINE1_U1 
    VBN = LINE1_U2 
    VCN = LINE1_U3 

    #3rd Harmonics
    IA_3rd = LINE1_IA3rd_Harm 
    IB_3rd = LINE1_IB3rd_Harm 
    IC_3rd = LINE1_IC3rd_Harm 
    VA_3rd = LINE1_VA3rd_Harm 
    VB_3rd = LINE1_VB3rd_Harm 
    VC_3rd = LINE1_VC3rd_Harm 

    #5th Harmonics
    IA_5th = LINE1_IA5th_Harm 
    IB_5th = LINE1_IB5th_Harm 
    IC_5th = LINE1_IC5th_Harm 
    VA_5th = LINE1_VA5th_Harm 
    VB_5th = LINE1_VB5th_Harm 
    VC_5th = LINE1_VC5th_Harm 
    
    return VA, VA_Ang, VB, VB_Ang, VC, VC_Ang, IN, IA, IA_Ang, IB, IB_Ang, IC, IC_Ang, VAB, VBC, VCA, VAN, VBN, VCN, IA_3rd, IB_3rd, IC_3rd, IA_5th, IB_5th, IC_5th, VA_3rd, VB_3rd, VC_3rd, VA_5th, VB_5th, VC_5th

@app.callback(
    [Output("VA-value", "children"),
     Output("VA_Ang-value", "children"),
     Output("VB-value", "children"),
     Output("VB_Ang-value", "children"),
     Output("VC-value", "children"),
     Output("VC_Ang-value", "children"),
     Output("IN-value", "children"),
     Output("IA-value", "children"),
     Output("IA_Ang-value", "children"),
     Output("IB-value", "children"),
     Output("IB_Ang-value", "children"),
     Output("IC-value", "children"),
     Output("IC_Ang-value", "children"),
     Output("VAB-value", "children"),
     Output("VBC-value", "children"),
     Output("VCA-value", "children"),
     Output("VAN-value", "children"),
     Output("VBN-value", "children"),
     Output("VCN-value", "children"),
     Output("IA_3rd-value", "children"),
     Output("IB_3rd-value", "children"),
     Output("IC_3rd-value", "children"),
     Output("IA_5th-value", "children"),
     Output("IB_5th-value", "children"),
     Output("IC_5th-value", "children"),
     Output("VA_3rd-value", "children"),
     Output("VB_3rd-value", "children"),
     Output("VC_3rd-value", "children"),
     Output("VA_5th-value", "children"),
     Output("VB_5th-value", "children"),
     Output("VC_5th-value", "children")],
    [Input("interval-component", "n_intervals")],
)
def update_voltage_current_values(n):
    # Panggil fungsi get_voltage_current() untuk mendapatkan nilai-nilai terbaru
    voltage_current_values = get_voltage_current()
    if voltage_current_values is not None:
        (VA, VA_Ang, VB, VB_Ang, VC, VC_Ang, IN, IA, IA_Ang, IB, IB_Ang, IC, IC_Ang, VAB, VBC, VCA, VAN, VBN, VCN, IA_3rd, IB_3rd, IC_3rd, IA_5th, IB_5th, IC_5th, VA_3rd, VB_3rd, VC_3rd, VA_5th, VB_5th, VC_5th) = voltage_current_values
        
        # Bulatkan nilai-nilai lainnya
        VA = round(VA, 3)
        VA_Ang = round(VA_Ang, 3)
        VB = round(VB, 3)
        VB_Ang = round(VB_Ang, 3)
        VC = round(VC, 3)
        VC_Ang = round(VC_Ang, 3)
        IN = round(IN, 3)
        IA = round(IA, 3)
        IA_Ang = round(IA_Ang, 3)
        IB = round(IB, 3)
        IB_Ang = round(IB_Ang, 3)
        IC = round(IC, 3)
        IC_Ang = round(IC_Ang, 3)
        VAB = round(VAB, 3)
        VBC = round(VBC, 3)
        VCA = round(VCA, 3)
        VAN = round(VAN, 3)
        VBN = round(VBN, 3)
        VCN = round(VCN, 3)
        IA_3rd = round(IA_3rd, 3)
        IB_3rd = round(IB_3rd, 3)
        IC_3rd = round(IC_3rd, 3)
        IA_5th = round(IA_5th, 3)
        IB_5th = round(IB_5th, 3)
        IC_5th = round(IC_5th, 3)
        VA_3rd = round(VA_3rd, 3)
        VB_3rd = round(VB_3rd, 3)
        VC_3rd = round(VC_3rd, 3)
        VA_5th = round(VA_5th, 3)
        VB_5th = round(VB_5th, 3)
        VC_5th = round(VC_5th, 3)

        # Send to Telegram if IN exceeds SETPOINT_IN
        if IN is not None and SETPOINT_IN is not None:
            send_telegram_alert(config, IN, SETPOINT_IN)

        return (VA, VA_Ang, VB, VB_Ang, VC, VC_Ang, IN, IA, IA_Ang, IB, IB_Ang, IC, IC_Ang, VAB, VBC, VCA, VAN, VBN, VCN, IA_3rd, IB_3rd, IC_3rd, IA_5th, IB_5th, IC_5th, VA_3rd, VB_3rd, VC_3rd, VA_5th, VB_5th, VC_5th)
    else:
        # Handle the case when voltage_current_values is None
        return ("N/A",) * 34

@app.callback(
    [Output("SETPOINT_IN-value", "children"),
     Output("Arus_Netral_beban_Normal-value", "children"),
     Output("Arus_Netral_beban_Puncak-value", "children")],
    [Input("setpoint-button", "n_clicks")],
    [State("SETPOINT_IN", "value"),
     State("IN_NL", "value"),
     State("IN_PL", "value")]
)
def update_card_values(n_clicks, setpoint_in, in_nl, in_pl):
    global SETPOINT_IN, IN_NL, IN_PL
    
    if n_clicks and setpoint_in is not None and in_nl is not None and in_pl is not None:
        # Ensure SETPOINT_IN is converted to float
        SETPOINT_IN = float(setpoint_in)
        IN_NL = float(in_nl)
        IN_PL = float(in_pl)

        return setpoint_in, in_nl, in_pl
    else:
        return dash.no_update, dash.no_update, dash.no_update
    
######################################################### Send Telegram Alert #####################################################################################
def send_telegram_alert(config, IN, SETPOINT_IN):
    # Telegram API endpoint for sending messages
    url = f"https://api.telegram.org/{config.telegram_bot_id}/sendMessage"
    
    # Check if IN exceeds SETPOINT_IN
    if IN > SETPOINT_IN:
        # Message to send
        message = f"Alert!!! IN value ({IN}) exceeded the SETPOINT_IN value ({SETPOINT_IN})!"
        
        # Parameters for the API request
        params = {
            "chat_id": config.telegram_chat_id,
            "text": message
        }
        
        # Send the alert
        response = requests.post(url, params=params)
        if response.status_code != 200:
            print("Failed to send alert to Telegram:", response.text)
            
# Run the app
if __name__ == '__main__':
    while True:
        run_mqtt_data_retrieval()
        run_mqtt_angle_retreival()
        run_mqtt_Vharm_retreival()
        run_mqtt_Iharm_retreival()
        process_data()
        app.run_server(debug=True, port=8050)
        