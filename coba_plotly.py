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
from utils import LineCalculation
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

# MQTT Broker information
# mqtt_broker = "broker.emqx.io"
# mqtt_topic = "topic/sensor_data"

try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["MVCS"]
    collection_LINE = db["LINE"]
    collection_Params = db["Params"]
    collection_Parameter = db["Parameter"]
    connected = True
except pymongo.errors.ConnectionFailure:
    connected = False

# config_folder = 'config_imp'
# config_files = [os.path.join(config_folder, f) for f in os.listdir(config_folder) if f.endswith('.json')]

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
filter_end_input = dbc.Row([
    html.Label("End Timestamp (YYYY-MM-DD_HH:MM:SS)", style={'color': 'white'}),
    html.Div([
        dbc.Input(type="Timestamp", id="end-time", placeholder="End Time", size="md", style={ 'background-color': 'white', 'border-color' : '#2AA198', 'border-width' : '5px'}),
    ]),
    dbc.Label("Enter End Time"),
],
    className="my-1",
)

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

Filter_button = html.Div(
    [
        dbc.Button("Filter Data", id="filter-button", color="success", className="me-1", n_clicks=0)
    ],
    className="d-grid gap-2 my-3",
)

csv_button = html.Div([
    html.Button("Save CSV", id="save-csv-button", className="btn btn-success me-1", n_clicks=0)
],
    className="d-grid gap-2 my-3",
)

filter_time = dbc.Form([filter_start_input, filter_end_input])

Apply_button = html.Div(
    [
        dbc.Button("Apply Changes", id="apply-button", size="sm", color="success", className="me-1", n_clicks=0)
    ],
    className="d-grid gap-2 my-3",
)

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

# Initialize data storage
# mqtt_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)
# Initialize data storage

# za_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)}
# zb_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)}
# zc_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)}

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
                page_size=20,  # Atur jumlah baris per halaman
            ),
        ]
    else:
        return []

def params():
    while True :
        # LINE1_U1 = 89236.961
        # LINE1_U2 = 89521.813
        # LINE1_U3 = 89844.727
        LINE1_Ang_U1 = 117.274
        LINE1_Ang_U2 = 356.92
        LINE1_Ang_U3 = 237.173

        INC_Data_IL = round(random.uniform(1, 20), 1)
        INC_Data_U = round(random.uniform(100, 200), 1)
        INC_Data_IL_Min = round(random.uniform(-20, -1),1)
        INC_Data_U_Min = round(random.uniform(-200, -100),1)

        LINE1_IL1 = 150 + INC_Data_IL + INC_Data_IL_Min
        LINE1_IL2 = 150 + INC_Data_IL + INC_Data_IL_Min
        LINE1_IL3 = 150 + INC_Data_IL + INC_Data_IL_Min
        LINE1_U1 = 800 + INC_Data_U + INC_Data_U_Min
        LINE1_U2 = 800 + INC_Data_U + INC_Data_U_Min
        LINE1_U3 = 800 + INC_Data_U + INC_Data_U_Min

        if LINE1_IL1 >= 200:
            LINE1_IL1 = 0
        
        # elif LINE1_IL2 >= 200:
        #     LINE1_IL2 = 0
        
        # elif LINE1_IL3 >= 200:
        #     LINE1_IL3 = 0

        LINE1_Ang_I1 = 112.977
        LINE1_Ang_I2 = 0.044
        LINE1_Ang_I3 = 232.82

        LINE1_z0z1_mag = 6.181
        LINE1_z0z1_ang = -2.55

        time.sleep(0.2)
        return LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3, LINE1_IL1, LINE1_IL2,\
                LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3, LINE1_z0z1_mag, LINE1_z0z1_ang
    
ZA_data = []

@app.callback(
    [Output('phase-to-gnd-graph', 'figure'),
     Output('phase-to-phase-graph', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('config-dropdown', 'value')])
def update_graphs(n, selected_config):
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

    # Update nilai-nilai dari utils.py menggunakan fungsi params()
    LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3, \
    LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3, \
    LINE1_z0z1_mag, LINE1_z0z1_ang = params()

    # Gunakan LineCalculation untuk mendapatkan data ZA
    line_calc = LineCalculation()  # Panggil LineCalculation di sini
    line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                                LINE1_z0z1_mag, LINE1_z0z1_ang)
    LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()

    # Menambahkan data baru ke ZA_data
    ZA_data.append((LINE1_ZA_Real, LINE1_ZA_Imag))
    # Periksa jika jumlah data ZA_data sudah mencapai 50
    if len(ZA_data) >= 50:
        # Hapus 1 data pertama dari ZA_data
        ZA_data.pop(0)

    # Perbarui dataframe df_ZA dengan 50 data terakhir
    df_ZA = pd.DataFrame(ZA_data[-50:], columns=['ZA_Real', 'ZA_Imag'])

    df_ZA['Frame'] = df_ZA.index

    # # Setelah pembaruan data ZA_data
    # ZA_Real_min = min(df_ZA['ZA_Real'])
    # ZA_Real_max = max(df_ZA['ZA_Real'])
    # ZA_Imag_min = min(df_ZA['ZA_Imag'])
    # ZA_Imag_max = max(df_ZA['ZA_Imag'])

    # # Tentukan faktor zoom in dan zoom out
    # zoom_factor = 0.0000000000000000000001

    # # Sesuaikan rentang sumbu x dan y
    # x_range = [ZA_Real_min - zoom_factor * (ZA_Real_max - ZA_Real_min),
    #         ZA_Real_max + zoom_factor * (ZA_Real_max - ZA_Real_min)]
    # y_range = [ZA_Imag_min - zoom_factor * (ZA_Imag_max - ZA_Imag_min),
    #         ZA_Imag_max + zoom_factor * (ZA_Imag_max - ZA_Imag_min)]

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
    fig_phase_to_gnd.add_trace(px.line(df_ZA, x="ZA_Real", y="ZA_Imag", color_discrete_sequence=['#1974D2'], 
                                      animation_group='Frame', markers=True).data[0])
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
    fig_phase_to_phase.add_trace(px.line(df_ZA, x="ZA_Real", y="ZA_Imag", color_discrete_sequence=['#1974D2'], 
                                      animation_group="Frame", markers=True).data[0])
    
    # Update layout
    fig_phase_to_phase.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.05)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'), #range=x_range),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)') #range=y_range)
    )
    
    # # Memeriksa apakah jumlah data dalam ZA_data melebihi maksimum yang diizinkan
    # if len(ZA_data) > max_data:
    #     # Menghitung berapa banyak data yang harus diganti
    #     replace_count = len(ZA_data) - max_data
        
    #     # Mengganti data awal dengan data baru secara berurutan
    #     for _ in range(replace_count):
    #         ZA_data.pop(0)

    # # Membuat list koordinat x dan y dari ZA_data
    # x = [point[0] for point in ZA_data]
    # y = [point[1] for point in ZA_data]

    # # Menentukan rentang sumbu x dan y sesuai dengan titik-titik ZA_data
    # x_range = [min(x), max(x)]
    # y_range = [min(y), max(y)]

    ## Scatter plot for MQTT data
    # mqtt_trace = go.Scatter(x=list(mqtt_data['x']),
    #                         y=list(mqtt_data['y']),
    #                         mode='lines+markers',
    #                         name='Voltage vs Current')
    
    # # Create scatter plot for Phase-to-Gnd
    # fig_phase_to_gnd = go.Figure()
    # fig_phase_to_gnd.add_trace(go.Scatter(
    #     x=config_x_phase_to_gnd,
    #     y=config_y_phase_to_gnd,
    #     mode='lines+markers',
    #     name='Config Data',
    #     marker=dict(color='white', size=5),
    #     line=dict(color='#03B77A', width=5),
    #     textfont=dict(color='white')
    # ))

    # fig_phase_to_gnd.add_trace(go.Scatter(
    #     x=x,
    #     y=y,
    #     mode='markers',
    #     name='ZA Data',
    #     marker=dict(color='#1974D2', size=10),
    #     # line=dict(color='#1974D2', width=3),
    #     textfont=dict(color='white')
    # ))
    # fig_phase_to_gnd.update_layout(
    #     title='Phase-to-Gnd',
    #     xaxis_title='Voltage',
    #     yaxis_title='Current',
    #     plot_bgcolor='rgba(0, 0, 0, 0)',
    #     paper_bgcolor='rgba(255, 255, 255, 0.05)',
    #     font=dict(color='white'),
    #     xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
    #     yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        # Set autoscale untuk zoom otomatis
        # xaxis_range=x_range,
        # yaxis_range=y_range
    # )

    # # Create scatter plot for Phase-to-Phase
    # fig_phase_to_phase = go.Figure()
    # fig_phase_to_phase.add_trace(go.Scatter(
    #     x=config_x_phase_to_phase,
    #     y=config_y_phase_to_phase,
    #     mode='lines+markers',
    #     name='Config Data',
    #     marker=dict(color='white', size=5),
    #     line=dict(color='#03B77A', width=5),
    #     textfont=dict(color='white')
    # ))
    # fig_phase_to_phase.add_trace(go.Scatter(
    #     x=x,
    #     y=y,
    #     mode='markers',
    #     name='ZA Data',
    #     marker=dict(color='#1974D2', size=10),
    #     # line=dict(color='#1974D2', width=3),
    #     textfont=dict(color='white')
    # ))
    # fig_phase_to_phase.update_layout(
    #     title='Phase-to-Phase',
    #     xaxis_title='Voltage',
    #     yaxis_title='Current',
    #     plot_bgcolor='rgba(0, 0, 0, 0)',
    #     paper_bgcolor='rgba(255, 255, 255, 0.05)',
    #     font=dict(color='white'),
    #     xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
    #     yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        # Set autoscale untuk zoom otomatis
        # xaxis_range=x_range,
        # yaxis_range=y_range
    # )
    # # Membuat DataFrame untuk phase_to_gnd
    # df_phase_to_gnd = pd.DataFrame({
    #     'Voltage': config_x_phase_to_gnd,
    #     'Current': config_y_phase_to_gnd
    # })

    # # Membuat DataFrame untuk phase_to_phase
    # df_phase_to_phase = pd.DataFrame({
    #     'Voltage': config_x_phase_to_phase,
    #     'Current': config_y_phase_to_phase
    # })
    
    # # Plot scatter plot untuk Phase-to-Gnd
    # fig_phase_to_gnd = px.scatter(df_phase_to_gnd, x=config_x_phase_to_gnd, y=config_y_phase_to_gnd, title='Phase-to-Gnd',
    #                             labels={'x': 'Voltage', 'y': 'Current'}, color_discrete_sequence=['white'])

    # # Atur warna dan gaya garis
    # fig_phase_to_gnd.update_traces(line=dict(color='green', width=2))

    # # Plot scatter plot untuk Phase-to-Phase
    # fig_phase_to_phase = px.scatter(df_phase_to_phase, x=config_x_phase_to_phase, y=config_y_phase_to_phase, title='Phase-to-Phase',
    #                                 labels={'x': 'Voltage', 'y': 'Current'}, color_discrete_sequence=['white'])

    # # Atur warna dan gaya garis
    # fig_phase_to_phase.update_traces(line=dict(color='green', width=2))

    # Kembalikan grafik yang diperbarui
    return fig_phase_to_gnd, fig_phase_to_phase

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
            
            # Mengembalikan nilai-nilai yang diperbarui agar ditampilkan di layout
            return float_values
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate
# # MQTT data reception
# def on_message(client, userdata, message):
#     data = json.loads(message.payload.decode())
#     voltage = data.get('voltage')
#     current = data.get('current')

#     if voltage is not None and current is not None:
#         mqtt_data['x'].append(voltage)
#         mqtt_data['y'].append(current)

# # Initialize MQTT client
# mqtt_client = mqtt.Client()
# mqtt_client.on_message = on_message
# mqtt_client.connect(mqtt_broker, 1883, 60)
# mqtt_client.subscribe(mqtt_topic)
# mqtt_client.loop_start()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)