import os
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
# MQTT Broker information
# mqtt_broker = "broker.emqx.io"
# mqtt_topic = "topic/sensor_data"

# Koneksi MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["MVCS"]
collection_LINE = db["LINE"]
collection_Params = db["Params"]
collection_Parameter = db["Parameter"]

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
    "Monitoring Voltage Current System", className="bg-transparent text-white p-2 mb-2 fs-1 text-center"
)

dropdown = html.Div(
    [
        html.Label('Select Config File :', style={'color': 'white'}),
        dcc.Dropdown(
            id='config-dropdown',
            options=[{'label': doc['_id'], 'value': doc['_id']} for doc in collection_LINE.find({})]
        ),
    ],
    className="mb-4",
)

dropdown2 = html.Div(
    [
        html.Label('Select Config File for Parameters :', style={'color': 'white'}),
        dcc.Dropdown(
            id='config-param-dropdown',
            options=[{'label': doc['_id'], 'value': doc['_id']} for doc in collection_Parameter.find({})]
        ),
    ],
    className="mb-1",
)

filter_start_input = dbc.Row([
    html.Label("Start Timestamp (YYYY-MM-DD_HH:MM:SS)", style={'color': 'white'}),
    html.Div(
        [
            dbc.Input(type="Timestamp", id="start-time", placeholder="Start Time", size="md", style={'background-color': 'white'}),
            dbc.Label("Enter Start Time"),
        ],
    ),
],
    className="my-1"
)
filter_end_input = dbc.Row([
    html.Label("End Timestamp (YYYY-MM-DD_HH:MM:SS)", style={'color': 'white'}),
    html.Div([
        dbc.Input(type="Timestamp", id="end-time", placeholder="End Time", size="md", style={'background-color': 'white'}),
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
                dbc.Input(type="Text", id="rgz1", size="sm", placeholder="RGZ1", style={ 'background-color': 'white'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rgz2", size="sm", placeholder="RGZ2", style={ 'background-color': 'white'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rgz3", size="sm", placeholder="RGZ3", style={ 'background-color': 'white'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter XGZ data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xgz1", size="sm", placeholder="XGZ1", style={ 'background-color': 'white'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xgz2", size="sm", placeholder="XGZ2", style={ 'background-color': 'white'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xgz3", size="sm", placeholder="XGZ3", style={ 'background-color': 'white'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter RPZ data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rpz1", size="sm", placeholder="RPZ1", style={ 'background-color': 'white'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rpz2", size="sm", placeholder="RPZ2", style={ 'background-color': 'white'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="rpz3", size="sm", placeholder="RPZ3", style={ 'background-color': 'white'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter XPZ data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xpz1", size="sm", placeholder="XPZ1", style={ 'background-color': 'white'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xpz2", size="sm", placeholder="XPZ2", style={ 'background-color': 'white'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="xpz3", size="sm", placeholder="XPZ3", style={ 'background-color': 'white'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter Angle data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="angle", size="sm", placeholder="Angle", style={ 'background-color': 'white'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="z0z1_mag", size="sm", placeholder="z0z1_mag", style={ 'background-color': 'white'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="z0z1_ang", size="sm", placeholder="z0z1_ang", style={ 'background-color': 'white'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter delta_t, id, line_length data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="delta_t", size="sm", placeholder="delta_t", style={ 'background-color': 'white'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="id2", size="sm", placeholder="id2", style={ 'background-color': 'white'})
            ], className="mx-1")
        ),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="line_length", size="sm", placeholder="line_length (KM)", style={ 'background-color': 'white'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter CT RATIO data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="CT_RATIO_HV", size="sm", placeholder="HV", style={ 'background-color': 'white'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="CT_RATIO_LV", size="sm", placeholder="LV", style={ 'background-color': 'white'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter VT RATIO data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="VT_RATIO_HV", size="sm", placeholder="HV", style={ 'background-color': 'white'})
            ], className="mx-1")
        ), 
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="VT_RATIO_LV", size="sm", placeholder="LV", style={ 'background-color': 'white'})
            ], className="mx-1")
        )
],
),
dbc.Row([
        html.Label("Enter CT/VT RATIO data ", style={'color': 'white'}),
        dbc.Col(
            html.Div([
                dbc.Input(type="Text", id="CTVT_RATIO", size="sm", placeholder="CT/VT Ratio", style={ 'background-color': 'white'})
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

control1 = dbc.Card(
    [dropdown, filter_time, 
     dbc.Row([
         dbc.Col(
            Filter_button
         ),
         dbc.Col(
            csv_button
         )
     ]
     ),    
         
         ],
    style={"height": 380, "width": 450},
    body=True,)

control2 = dbc.Card([
    dropdown2,line_param],
    style={"height": 650, "width": 450},
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
                                            ],  width=20, ),
                                            dbc.Col([
                                                control2,
                                                # ************************************
                                                # Uncomment line below when running locally!
                                                # ************************************
                                                # theme_controls
                                            ],  width=20, className="my-4"),
                                        ]),
                                 # Display warning message if no configuration file is selected
                                html.Div(id='warning-message', children=[]),
                                html.Div([
                                    html.Div(id='line_param'),
                                    html.Button('Apply Changes', id='apply-button', n_clicks=0),
                                    html.Div(id='output-message')
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
                page_size=10,  # Atur jumlah baris per halaman
            ),
        ]
    else:
        return []

    
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
    LINE1_z0z1_mag, LINE1_z0z1_ang = utils.params()

    # Gunakan LineCalculation untuk mendapatkan data ZA
    line_calc = LineCalculation()  # Panggil LineCalculation di sini
    line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                                LINE1_z0z1_mag, LINE1_z0z1_ang)
    LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()

    # Tambahkan nilai ZA ke dalam daftar ZA_data
    ZA_data.append((LINE1_ZA_Real, LINE1_ZA_Imag))

    ## Scatter plot for MQTT data
    # mqtt_trace = go.Scatter(x=list(mqtt_data['x']),
    #                         y=list(mqtt_data['y']),
    #                         mode='lines+markers',
    #                         name='Voltage vs Current')
    
    # Create scatter plot for Phase-to-Gnd
    fig_phase_to_gnd = go.Figure()
    fig_phase_to_gnd.add_trace(go.Scatter(
        x=config_x_phase_to_gnd,
        y=config_y_phase_to_gnd,
        mode='lines+markers',
        name='Config Data',
        marker=dict(color='white', size=5),
        line=dict(color='green', width=5),
        textfont=dict(color='white')
    ))
    fig_phase_to_gnd.add_trace(go.Scatter(
        x=[point[0] for point in ZA_data],
        y=[point[1] for point in ZA_data],
        mode='markers',
        name='ZA Data',
        marker=dict(color='red', size=5),
        textfont=dict(color='white')
    ))
    fig_phase_to_gnd.update_layout(
        title='Phase-to-Gnd',
        xaxis_title='Voltage',
        yaxis_title='Current',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.05)',
        font=dict(color='white')
    )

    # Create scatter plot for Phase-to-Phase
    fig_phase_to_phase = go.Figure()
    fig_phase_to_phase.add_trace(go.Scatter(
        x=config_x_phase_to_phase,
        y=config_y_phase_to_phase,
        mode='lines+markers',
        name='Config Data',
        marker=dict(color='white', size=5),
        line=dict(color='green', width=5),
        textfont=dict(color='white')
    ))
    fig_phase_to_phase.add_trace(go.Scatter(
        x=[point[0] for point in ZA_data],
        y=[point[1] for point in ZA_data],
        mode='markers',
        name='ZA Data',
        marker=dict(color='red', size=5),
        textfont=dict(color='white')
    ))
    fig_phase_to_phase.update_layout(
        title='Phase-to-Phase',
        xaxis_title='Voltage',
        yaxis_title='Current',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.05)',
        font=dict(color='white')
    )

    # Kembalikan grafik yang diperbarui
    return fig_phase_to_gnd, fig_phase_to_phase

# Callback untuk menyimpan data yang difilter ke dalam file CSV
@app.callback(
    Output('save-csv-message', 'children'),
    [Input('save-csv-button', 'n_clicks')],
    [State('start_time', 'value'),
     State('end_time', 'value')]
)
def save_filtered_data_to_csv(n_clicks, start_time, end_time):
    if n_clicks > 0 and start_time and end_time:
        # Ambil data dari MongoDB dalam rentang waktu timestamp yang ditentukan
        filtered_data = collection_Params.find({"Timestamp": {"$gte": start_time, "$lte": end_time}})
        
        # Ubah data yang diambil ke dalam DataFrame
        df = pd.DataFrame(list(filtered_data))
        
        # Buat nama file dengan timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"filter_data_{timestamp}.csv"
        
        # Tentukan direktori untuk menyimpan file CSV
        save_folder = 'data_csv'
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        
        # Simpan DataFrame ke dalam file CSV
        csv_path = os.path.join(save_folder, filename)
        df.to_csv(csv_path, index=False)
        
        return html.Div(f"Data filtered successfully saved to {csv_path}", style={'color': 'green'})

# Callback to initialize input values based on MongoDB data
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
    Input('config-param-dropdown', 'value')
)
def initialize_input_values(selected_config):
    if selected_config:
        parameter_data = collection_Parameter.find_one({"_id": selected_config})
        if parameter_data:
            return (
                parameter_data.get('rgz1', ''),
                parameter_data.get('rgz2', ''),
                parameter_data.get('rgz3', ''),
                parameter_data.get('xgz1', ''),
                parameter_data.get('xgz2', ''),
                parameter_data.get('xgz3', ''),
                parameter_data.get('rpz1', ''),
                parameter_data.get('rpz2', ''),
                parameter_data.get('rpz3', ''),
                parameter_data.get('xpz1', ''),
                parameter_data.get('xpz2', ''),
                parameter_data.get('xpz3', ''),
                parameter_data.get('angle', ''),
                parameter_data.get('z0z1_mag', ''),
                parameter_data.get('z0z1_ang', ''),
                parameter_data.get('delta_t', ''),
                parameter_data.get('id2', ''),
                parameter_data.get('line_length', ''),
                parameter_data.get('CT_RATIO_HV', ''),
                parameter_data.get('CT_RATIO_LV', ''),
                parameter_data.get('VT_RATIO_HV', ''),
                parameter_data.get('VT_RATIO_LV', ''),
                parameter_data.get('CTVT_RATIO', '')
            )
    # Return empty strings if no config is selected or if no data found in MongoDB
    return ('',) * 23 # 24 output values, all initialized to empty string

# Callback to update parameter values in MongoDB
@app.callback(
    Output('output-message', 'children'),
    [Input('apply-button', 'n_clicks')],
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
        # Mengonversi nilai menjadi int32 jika tidak kosong
        int_values = [int(val) if val is not None and val != '' else None for val in [rgz1, rgz2, rgz3, xgz1, xgz2, xgz3, rpz1, rpz2, rpz3, xpz1, xpz2, xpz3, angle, z0z1_mag, z0z1_ang, delta_t, id2, line_length, CT_RATIO_HV, CT_RATIO_LV, VT_RATIO_HV, VT_RATIO_LV, CTVT_RATIO]]
        
        if all(value is not None for value in int_values) and selected_config:
            parameter_id = selected_config  
            # Update parameter values directly into Parameter collection
            collection_Parameter.update_one({'_id': parameter_id}, {'$set': {'rgz1': int_values[0], 'rgz2': int_values[1], 'rgz3': int_values[2], 'xgz1': int_values[3], 'xgz2': int_values[4], 'xgz3': int_values[5], 'rpz1': int_values[6], 'rpz2': int_values[7], 'rpz3': int_values[8], 'xpz1': int_values[9], 'xpz2': int_values[10], 'xpz3': int_values[11], 'angle': int_values[12], 'z0z1_mag': int_values[13], 'z0z1_ang': int_values[14], 'delta_t': int_values[15], 'id2': int_values[16], 'line_length': int_values[17], 'CT_RATIO_HV': int_values[18], 'CT_RATIO_LV': int_values[19], 'VT_RATIO_HV': int_values[20], 'VT_RATIO_LV': int_values[21], 'CTVT_RATIO': int_values[22]}})
            return html.Div([
                html.P('Parameters updated successfully', style={'color': 'green'})
            ])
        else:
            return html.Div([
                html.P('No data changes', style={'color': 'red'})
            ])

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