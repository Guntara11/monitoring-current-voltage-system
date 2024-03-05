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
import utils
from utils import LineCalculation, ZoneCalculation
import pymongo
import pandas as pd
import dash_ag_grid as dag
from datetime import datetime
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from dash.exceptions import PreventUpdate
import time
import random
import plotly.express as px
import dash_daq as daq
from mqtt_Client import MQTTClient
from get_mqtt_data import ZA_data, process_Mag_data

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
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR], suppress_callback_exceptions=True)

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
                dbc.Input(type="Text", id="rgz1", size="sm", placeholder="RGZ1", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rgz2", size="sm", placeholder="RGZ2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rgz3", size="sm", placeholder="RGZ3", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter XGZ data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xgz1", size="sm", placeholder="XGZ1", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xgz2", size="sm", placeholder="XGZ2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xgz3", size="sm", placeholder="XGZ3", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter RPZ data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rpz1", size="sm", placeholder="RPZ1", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rpz2", size="sm", placeholder="RPZ2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rpz3", size="sm", placeholder="RPZ3", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter XPZ data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xpz1", size="sm", placeholder="XPZ1", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xpz2", size="sm", placeholder="XPZ2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xpz3", size="sm", placeholder="XPZ3", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter Angle data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="angle", size="sm", placeholder="Angle", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="z0z1_mag", size="sm", placeholder="z0z1_mag", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="z0z1_ang", size="sm", placeholder="z0z1_ang", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter delta_t, id, line_length data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="delta_t", size="sm", placeholder="delta_t", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="id2", size="sm", placeholder="id2", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="line_length", size="sm", placeholder="line_length (KM)", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter CT RATIO data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="CT_RATIO_HV", size="sm", placeholder="HV", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="CT_RATIO_LV", size="sm", placeholder="LV", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter VT RATIO data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="VT_RATIO_HV", size="sm", placeholder="HV", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="VT_RATIO_LV", size="sm", placeholder="LV", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter CT/VT RATIO data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="CTVT_RATIO", size="sm", placeholder="CT/VT Ratio", style={ 'background-color': 'white', "border-color": "#2AA198", "border-width": "5px"})
            ], className="mx-1")
        ), 
],
),
])

#Apply Changes Button
Apply_button = html.Div(
    [
        dbc.Button("Apply Changes", id="apply-button", size="sm", color="success", className="me-1", n_clicks=0)
    ],
    className="d-grid gap-2 my-3",
)

#Filter Button
Filter_button = html.Div(
    [
        dbc.Button("Filter Data", id="filter-button", color="success", className="me-1", n_clicks=0)
    ],
    className="d-grid gap-2 my-3",
)

# Save CSV Button
csv_button = html.Div([
    html.Button("Save CSV", id="save-csv-button", className="btn btn-success me-1", n_clicks=0)
],
    className="d-grid gap-2 my-3",
)

filter_time = dbc.Form([filter_start_input, filter_end_input])

#Card control1
control1 = dbc.Card(
    [dropdown, filter_time, 
     dbc.Row([
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
    style={"height": 450, "width": 400},
    body=True,
)

# Card control2
control2 = dbc.Card([
    dropdown2,line_param, 
    dbc.Row([
         dbc.Col(
            Apply_button
         )
     ]
     ),    
        ],
    style={"height": 740, "width": 400},
    body=True,)

# Card voltage an current values
card_voltage = dbc.Card(
    [
        dbc.CardBody(
        [
            html.H4("Voltage", className="card-title", 
                    style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '20px'}),
            html.H2(id="voltage-value", className="card-subtitle mb-2 text-muted", 
                    style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '28px'}),
        ]
        )
    ],
)

card_current = dbc.Card(
    [
        dbc.CardBody(
        [
            html.H4("Current", className="card-title", 
                    style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '20px'}),
            html.H2(id="current-value", className="card-subtitle mb-2 text-muted", 
                    style={'color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '28px'}),
        ]
        )
    ],
)

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
                                    card_voltage,
                                ],  width=6,
                                style={'margin-bottom': '5mm','color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '28px'}
                                ),
                                dbc.Col([
                                    card_current,
                                ],  width=6,
                                style={'margin-bottom': '5mm','color': '#00FF00', 'fontFamily': 'Electrolize, sans-serif', 'fontSize': '28px'}
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

# Fungsi untuk menghasilkan nilai tegangan dan arus secara acak
def get_voltage_current_value():
    voltage_value = random.uniform(200, 240)
    current_value = random.uniform(3, 7)
    return voltage_value, current_value

# Callback for filtering data based on timestamps
@app.callback(
    Output('mongo-datatable', 'children'),
    [Input('filter-button', 'n_clicks')],
    [State('start-time', 'value'),
     State('end-time', 'value')]
)

def filter_data(n_clicks, start_time, end_time):
    if n_clicks and start_time and end_time:
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
        ]
    else:
        return []

mag_data = process_Mag_data()
ZA_Real, ZA_Imag = ZA_data(mag_data)

# Update Graph
@app.callback(
    [Output('phase-to-gnd-graph', 'figure'),
     Output('phase-to-phase-graph', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('config-dropdown', 'value')],
    [State('phase-to-gnd-graph', 'relayoutData'),
     State('phase-to-phase-graph', 'relayoutData')])

def update_graphs(n, selected_config, relayout_data_gnd, relayout_data_phase):
    # Periksa apakah nilai selected_config tidak kosong
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
    
    # Plot ZA_Data
    fig_phase_to_gnd.add_trace(px.line(df_ZA, x="ZA_Real", y="ZA_Imag", color_discrete_sequence=['#1974D2'], markers=True).data[0])
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

    #plot ZA_DAta
    fig_phase_to_phase.add_trace(px.line(df_ZA, x="ZA_Real", y="ZA_Imag", color_discrete_sequence=['#1974D2'], markers=True).data[0])
    
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
    
# Save Data CSV
@app.callback(
    Output('save-csv-button', 'n_clicks'),
    [Input('filter-button', 'n_clicks')],
    [State('start-time', 'value'),
     State('end-time', 'value')]
)
def save_csv(n_clicks, start_time, end_time):
    if n_clicks and start_time and end_time:
        filtered_data = collection_Params.find({"Timestamp": {"$gte": start_time, "$lte": end_time}})
        df = pd.DataFrame(list(filtered_data))
        
        # Buat folder jika belum ada
        folder_path = "data_csv"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Buat nama file CSV dengan format yang diinginkan
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(folder_path, f"filter_data_{timestamp}.csv")
        
        # Menyimpan DataFrame ke dalam file CSV
        df.to_csv(filename, index=False)
        return 0  # Mengatur kembali nilai n_clicks tombol "Save CSV" menjadi 0
    else:
        raise PreventUpdate

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
    if n_clicks is not None and n_clicks > 0:
        # Mengonversi nilai menjadi float jika tidak kosong
        float_values = [float(val) if val is not None and val != '' else None for val in [rgz1, rgz2, rgz3, xgz1, xgz2, xgz3, rpz1, rpz2, rpz3, xpz1, xpz2, xpz3, angle, z0z1_mag, z0z1_ang, delta_t, id2, line_length, CT_RATIO_HV, CT_RATIO_LV, VT_RATIO_HV, VT_RATIO_LV, CTVT_RATIO]]
        
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
                            "kanan_bawah_z3": {"x": pp_down_right_z3_x, "y": pp_down_right_z3_y}
                        }
                    }

                    collection_LINE.update_one({'_id': parameter_id}, {'$set': line_data}, upsert=True)

                    return float_values[0], float_values[1], float_values[2], float_values[3], float_values[4], float_values[5], float_values[6], float_values[7], float_values[8], float_values[9], float_values[10], float_values[11], float_values[12], float_values[13], float_values[14], float_values[15], float_values[16], float_values[17], float_values[18], float_values[19], float_values[20], float_values[21], float_values[22]
    return None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
# Callback untuk memperbarui nilai tegangan dan arus setiap detik
@app.callback(
    [Output("voltage-value", "children"),
     Output("current-value", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_values(n):
    voltage_value, current_value = get_voltage_current_value()
    return f"{voltage_value:.2f} V", f"{current_value:.2f} A"

# Run the app
if __name__ == '__main__':
    while True:
        # run_mqtt_data_retrieval()
        app.run_server(debug=True, port=8050)
        time.sleep(0.2)