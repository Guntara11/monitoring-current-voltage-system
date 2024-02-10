import os
import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import paho.mqtt.client as mqtt
import plotly.graph_objs as go
from collections import deque

# MQTT Broker information
mqtt_broker = "broker.emqx.io"
mqtt_topic = "topic/sensor_data"

# Folder containing JSON configuration files
config_folder = 'config_imp'
config_files = [os.path.join(config_folder, f) for f in os.listdir(config_folder) if f.endswith('.json')]

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div(
    [
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

        dcc.Interval(
            id='interval-component',
            interval=1*1000,  # in milliseconds
            n_intervals=0
        ),
    ]
)

# Initialize data storage for MQTT data
mqtt_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)}

@app.callback(
    [Output('phase-to-gnd-graph', 'figure'),
     Output('phase-to-phase-graph', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('config-dropdown-phase-to-gnd', 'value'),
     Input('config-dropdown-phase-to-phase', 'value')])

def update_graph(n, selected_config_phase_to_gnd, selected_config_phase_to_phase):
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

    # Scatter plot for MQTT data
    mqtt_trace = go.Scatter(x=list(mqtt_data['x']),
                            y=list(mqtt_data['y']),
                            mode='lines+markers',
                            name='Voltage vs Current')

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

    return {'data': [mqtt_trace, config_trace_phase_to_gnd, lines_trace_phase_to_gnd], 'layout': layout_phase_to_gnd}, \
           {'data': [mqtt_trace, config_trace_phase_to_phase, lines_trace_phase_to_phase], 'layout': layout_phase_to_phase}


# MQTT data reception
def on_message(client, userdata, message):
    data = json.loads(message.payload.decode())
    voltage = data.get('voltage')
    current = data.get('current')

    if voltage is not None and current is not None:
        mqtt_data['x'].append(voltage)
        mqtt_data['y'].append(current)

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, 1883, 60)
mqtt_client.subscribe(mqtt_topic)
mqtt_client.loop_start()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
