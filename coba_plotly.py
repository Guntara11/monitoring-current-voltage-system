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
# MQTT Broker information
# mqtt_broker = "broker.emqx.io"
# mqtt_topic = "topic/sensor_data"

# Ganti URL koneksi dengan URL koneksi MongoDB Atlas Anda
client = pymongo.MongoClient("mongodb+srv://sopiand23:Manusiakuat1@mycluster.bfapaaq.mongodb.net/")
db = client["MyData"]
collection = db["MyCollect"]

config_folder = 'config_imp'
config_files = [os.path.join(config_folder, f) for f in os.listdir(config_folder) if f.endswith('.json')]


# Initialize Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR], suppress_callback_exceptions=True)

# Layout of the dashboard

app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H1('Monitoring Voltage Current System', style={'textAlign': 'center', 'color': 'white'}))),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Nav(
                            [
                                dbc.NavItem(
                                    [
                                        html.Label('Select Config File (Phase-to-Gnd):', style={'color': 'white'}),
                                        dcc.Dropdown(
                                            id='config-dropdown-phase-to-gnd',
                                            options=[{'label': f, 'value': f} for f in config_files],
                                            value=config_files[0] if config_files else None
                                        ),
                                    ],
                                    className='mb-3'
                                ),
                                dbc.NavItem(
                                    [
                                        html.Label('Select Config File (Phase-to-Phase):', style={'color': 'white'}),
                                        dcc.Dropdown(
                                            id='config-dropdown-phase-to-phase',
                                            options=[{'label': f, 'value': f} for f in config_files],
                                            value=config_files[0] if config_files else None
                                        ),
                                    ],
                                    className='mb-3'
                                ),
                                dbc.NavItem(
                                    [
                                        html.Label('Start Timestamp (YYYY-MM-DD_HH:MM:SS):', style={'color': 'white'}),
                                        dcc.Input(id='start-time', type='text', placeholder='Start Timestamp'),
                                    ],
                                    className='mb-3'
                                ),
                                dbc.NavItem(
                                    [
                                        html.Label('End Timestamp (YYYY-MM-DD_HH:MM:SS):', style={'color': 'white'}),
                                        dcc.Input(id='end-time', type='text', placeholder='End Timestamp'),
                                    ],
                                    className='mb-3'
                                ),
                                dbc.NavItem(
                                    [
                                        html.Button('Filter Data', id='filter-button', n_clicks=0),
                                    ],
                                    className='mb-3'
                                ),
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
    if n_clicks > 0 and start_time and end_time:
        # Fetch data from MongoDB within the specified timestamp range
        filtered_data = collection.find({"Timestamp": {"$gte": start_time, "$lte": end_time}})
        
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


@app.callback(
    Output('phase-to-gnd-graph', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('config-dropdown-phase-to-gnd', 'value')])
def update_phase_to_gnd_graph(n, selected_config_phase_to_gnd):
    if not selected_config_phase_to_gnd:
        return {}
    
    # Read configuration data from the selected config file for phase-to-gnd
    with open(selected_config_phase_to_gnd) as config_file_phase_to_gnd:
        config_data_phase_to_gnd = json.load(config_file_phase_to_gnd)

    # Extract x and y values from config data
    config_x_phase_to_gnd = [config_data_phase_to_gnd[key]['x'] for key in config_data_phase_to_gnd]
    config_y_phase_to_gnd = [config_data_phase_to_gnd[key]['y'] for key in config_data_phase_to_gnd]

    # Use LineCalculation to get ZA data
    line_calc = LineCalculation()
    line_calc.calculate_values(utils.LINE1_U1, utils.LINE1_U2, utils.LINE1_U3, utils.LINE1_Ang_U1, utils.LINE1_Ang_U2, utils.LINE1_Ang_U3,
                                utils.LINE1_IL1, utils.LINE1_IL2, utils.LINE1_IL3, utils.LINE1_Ang_I1, utils.LINE1_Ang_I2, utils.LINE1_Ang_I3,
                                utils.LINE1_z0z1_mag, utils.LINE1_z0z1_ang)
    LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()
    
    # # Scatter plot for MQTT data
    # mqtt_trace = go.Scatter(x=list(mqtt_data['x']),
    #                         y=list(mqtt_data['y']),
    #                         mode='lines+markers',
    #                         name='Voltage vs Current')

    # Create scatter plot
    fig = go.Figure()
    # Add scatter plot for config data
    fig.add_trace(go.Scatter(
        x=config_x_phase_to_gnd, 
        y=config_y_phase_to_gnd, 
        mode='lines+markers',  # Mode untuk menampilkan garis dan titik
        name='Config Data', 
        marker=dict(color='white', size=5),
        line=dict(color='green', width=5),
        textfont=dict(color='white')
    ))

    # Add scatter plot for ZA data
    fig.add_trace(go.Scatter(
        x=[LINE1_ZA_Real], 
        y=[LINE1_ZA_Imag], 
        mode='markers', 
        name='ZA Data', 
        marker=dict(color='red', size=5),
        textfont=dict(color='white')
    ))
    
    # Set title and axis labels
    fig.update_layout(
        title='Phase-to-Gnd',
        xaxis_title='Voltage',
        yaxis_title='Current',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.05)',
        font=dict(color='white')
    )

    return fig

# Callback to update the Phase-to-Phase graph
@app.callback(
    Output('phase-to-phase-graph', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('config-dropdown-phase-to-phase', 'value')])
def update_phase_to_phase_graph(n, selected_config_phase_to_phase):
    if not selected_config_phase_to_phase:
        return {}
    
    # Read configuration data from the selected config file for phase-to-phase
    with open(selected_config_phase_to_phase) as config_file_phase_to_phase:
        config_data_phase_to_phase = json.load(config_file_phase_to_phase)

    # Extract x and y values from config data
    config_x_phase_to_phase = [config_data_phase_to_phase[key]['x'] for key in config_data_phase_to_phase]
    config_y_phase_to_phase = [config_data_phase_to_phase[key]['y'] for key in config_data_phase_to_phase]

    # Use LineCalculation to get ZA data
    line_calc = LineCalculation()
    line_calc.calculate_values(utils.LINE1_U1, utils.LINE1_U2, utils.LINE1_U3, utils.LINE1_Ang_U1, utils.LINE1_Ang_U2, utils.LINE1_Ang_U3,
                                utils.LINE1_IL1, utils.LINE1_IL2, utils.LINE1_IL3, utils.LINE1_Ang_I1, utils.LINE1_Ang_I2, utils.LINE1_Ang_I3,
                                utils.LINE1_z0z1_mag, utils.LINE1_z0z1_ang)
    LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()

    # # Scatter plot for MQTT data
    # mqtt_trace = go.Scatter(x=list(mqtt_data['x']),
    #                         y=list(mqtt_data['y']),
    #                         mode='lines+markers',
    #                         name='Voltage vs Current')
    
    # Create scatter plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=config_x_phase_to_phase, 
        y=config_y_phase_to_phase, 
        mode='lines+markers',  # Mode untuk menampilkan garis dan titik
        name='Config Data', 
        marker=dict(color='white', size=5),
        line=dict(color='green', width=5),
        textfont=dict(color='white') 
    ))

    # Add scatter plot for ZA data
    fig.add_trace(go.Scatter(
        x=[LINE1_ZA_Real], 
        y=[LINE1_ZA_Imag], 
        mode='markers', 
        name='ZA Data', 
        marker=dict(color='red', size=5),
        textfont=dict(color='white')
    ))

    # Set title and axis labels
    fig.update_layout(
        title='Phase-to-Phase',
        xaxis_title='Voltage',
        yaxis_title='Current',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.05)',
        font=dict(color='white')
    )

    return fig

    # return {'data': [config_trace], 'layout': layout}

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
    app.run_server(debug=True)