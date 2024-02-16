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
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Layout of the dashboard

app.layout = html.Div(
    [
        html.H1('Monitoring Voltage Current System', style={'textAlign': 'center'}),
        dcc.Interval(id='interval_db', interval=86400000, n_intervals=0),
        html.Div(
            [
                html.Label('Select Config File:'),
                dcc.Dropdown(
                    id='config-dropdown-phase-to-gnd',
                    options=[{'label': f, 'value': f} for f in config_files],
                    value=config_files[0] if config_files else None
                ),
                dcc.Graph(id='phase-to-gnd-graph')
            ],
            style={'width': '49%', 'display': 'inline-block'}
        ),

        html.Div(
            [
                html.Label('Select Config File:'),
                dcc.Dropdown(
                    id='config-dropdown-phase-to-phase',
                    options=[{'label': f, 'value': f} for f in config_files],
                    value=config_files[0] if config_files else None
                ),
                dcc.Graph(id='phase-to-phase-graph')
            ],
            style={'width': '49%', 'display': 'inline-block'}
        
        ),
        html.Div([
            dcc.Input(id='start-time', type='text', placeholder='Start Timestamp (YYYY-MM-DD_HH:MM:SS)'),
            dcc.Input(id='end-time', type='text', placeholder='End Timestamp (YYYY-MM-DD_HH:MM:SS)'),
            html.Button('Filter Data', id='filter-button', n_clicks=0)
        ]),
        html.Div(id='mongo-datatable', children=[]),
        dcc.Interval(
            id='interval-component',
            interval=1*100,  # in milliseconds
            n_intervals=0
        ),
    ]
)

# Initialize data storage
# mqtt_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)
# Initialize data storage

# za_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)}
# zb_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)}
# zc_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)}

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
                id='mongo-datatable',
                data=df.to_dict('records'),
                columns=[{'id': p, 'name': p, 'editable': False} if p == '_id'
                         else {'id': p, 'name': p, 'editable': True}
                         for p in df.columns],
            ),
        ]
    else:
        return []



@app.callback(
    [Output('phase-to-gnd-graph', 'figure'),
     Output('phase-to-phase-graph', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('config-dropdown-phase-to-gnd', 'value'),
     Input('config-dropdown-phase-to-phase', 'value')])



def update_graph(n, selected_config_phase_to_gnd, selected_config_phase_to_phase):
    line_calc = LineCalculation()
    line_calc.calculate_values(utils.LINE1_U1, utils.LINE1_U2, utils.LINE1_U3, utils.LINE1_Ang_U1, utils.LINE1_Ang_U2, utils.LINE1_Ang_U3,
                                    utils.LINE1_IL1, utils.LINE1_IL2, utils.LINE1_IL3, utils.LINE1_Ang_I1, utils.LINE1_Ang_I2, utils.LINE1_Ang_I3,
                                    utils.LINE1_z0z1_mag, utils.LINE1_z0z1_ang)
    LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()
    
    if not selected_config_phase_to_gnd or not selected_config_phase_to_phase:
        return {}, {}

    # Read configuration data from the selected config file for phase-to-gnd
    with open(selected_config_phase_to_gnd) as config_file_phase_to_gnd:
        config_data_phase_to_gnd = json.load(config_file_phase_to_gnd)

    config_keys_phase_to_gnd = list(config_data_phase_to_gnd.keys())
    config_x_phase_to_gnd = [config_data_phase_to_gnd[key]['x'] for key in config_data_phase_to_gnd]
    config_y_phase_to_gnd = [config_data_phase_to_gnd[key]['y'] for key in config_data_phase_to_gnd]

    # Read configuration data from the selected config file for phase-to-phase
    with open(selected_config_phase_to_phase) as config_file_phase_to_phase:
        config_data_phase_to_phase = json.load(config_file_phase_to_phase)

    config_keys_phase_to_phase = list(config_data_phase_to_phase.keys())
    config_x_phase_to_phase = [config_data_phase_to_phase[key]['x'] for key in config_data_phase_to_phase]
    config_y_phase_to_phase = [config_data_phase_to_phase[key]['y'] for key in config_data_phase_to_phase]
    
    # # Scatter plot for MQTT data
    # mqtt_trace = go.Scatter(x=list(mqtt_data['x']),
    #                         y=list(mqtt_data['y']),
    #                         mode='lines+markers',
    #                         name='Voltage vs Current')
    za_trace = go.Scatter(x=[LINE1_ZA_Real], 
                          y=[LINE1_ZA_Imag], 
                          mode='markers', 
                          name='ZA', 
                          marker=dict(size=10, color='blue'))
    
    
    # Scatter plot for config data for phase-to-gnd
    config_trace_phase_to_gnd = go.Scatter(x=config_x_phase_to_gnd, y=config_y_phase_to_gnd,
                                            mode='markers',
                                            name='Config Points (Phase-to-Gnd)',
                                            marker=dict(color='red', size=10))

    # Scatter plot for config data for phase-to-phase
    config_trace_phase_to_phase = go.Scatter(x=config_x_phase_to_phase, y=config_y_phase_to_phase,
                                              mode='markers',
                                              name='Config Points (Phase-to-Phase)',
                                              marker=dict(color='blue', size=10))

    # Lines to connect specific points for phase-to-gnd
    lines_trace_phase_to_gnd = go.Scatter(x=config_x_phase_to_gnd, y=config_y_phase_to_gnd,
                                          mode='lines',
                                          name='Lines (Phase-to-Gnd)',
                                          line=dict(color='green', width=2))

    # Lines to connect specific points for phase-to-phase
    lines_trace_phase_to_phase = go.Scatter(x=config_x_phase_to_phase, y=config_y_phase_to_phase,
                                             mode='lines',
                                             name='Lines (Phase-to-Phase)',
                                             line=dict(color='orange', width=2))

    layout_phase_to_gnd = go.Layout(title='Live Dashboard - Voltage vs Current with Config Points (Phase-to-Gnd)',
                                    xaxis=dict(title='Voltage'),
                                    yaxis=dict(title='Current'),
                                    showlegend=True,
                                    width=1250,
                                    height=850)

    layout_phase_to_phase = go.Layout(title='Live Dashboard - Voltage vs Current with Config Points (Phase-to-Phase)',
                                      xaxis=dict(title='Voltage'),
                                      yaxis=dict(title='Current'),
                                      showlegend=True,
                                      width=1250,
                                      height=850)

    return {'data': [za_trace, config_trace_phase_to_gnd, lines_trace_phase_to_gnd], 'layout': layout_phase_to_gnd}, \
           {'data': [za_trace, config_trace_phase_to_phase, lines_trace_phase_to_phase], 'layout': layout_phase_to_phase}

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