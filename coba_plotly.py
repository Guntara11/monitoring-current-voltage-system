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



# # Read configuration data from config.json
# with open('config.json') as config_file:
#     config_data = json.load(config_file)


# Extract x and y coordinates and keys from config data
# config_keys = list(config_data.keys())
# config_x = [config_data[key]['x'] for key in config_data]
# config_y = [config_data[key]['y'] for key in config_data]

config_folder = 'config_imp'
config_files = [os.path.join(config_folder, f) for f in os.listdir(config_folder) if f.endswith('.json')]

# lines_kanan = ["kanan_bawah_z1","kanan_samping_z1", "kanan_samping_z2", "kanan_samping_z3"]
# lines_kiri = ["kiri_atas_z3","kiri_samping_z1", "kiri_samping_z2", "kiri_samping_z3"]
# lines_atas = ["kiri_atas_z3", "reach_z3", "kanan_samping_z3"]
# lines_bawah = ["kiri_bawah_z1", "point", "kanan_bawah_z1"]
# lines_tengah0 = ["point", "reach_z1", "reach_z2", "reach_z3"]
# lines_tengah1=["kiri_atas_z1", "reach_z1", "kanan_atas_z1"]
# lines_tengah2=["kiri_atas_z2", "reach_z2", "kanan_samping_z2"]

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
# Layout of the dashboard
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

# Initialize data storage
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
#  # Add text annotations for config points
#     annotations = [dict(x=x, y=y, text=key, showarrow=True, arrowhead=2, arrowcolor='black', arrowsize=1)
#                    for key, x, y in zip(config_keys, config_x, config_y)]
    
    # # Lines to connect specific points
    # lines_kanan_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_kanan],
    #                         y=[config_data[key]['y'] for key in lines_kanan],
    #                         mode='lines',
    #                         name='Lines',
    #                         line=dict(color='blue', width=2))
    # lines_kiri_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_kiri],
    #                         y=[config_data[key]['y'] for key in lines_kiri],
    #                         mode='lines',
    #                         name='Lines',
    #                         line=dict(color='blue', width=2))
    # lines_atas_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_atas],
    #                         y=[config_data[key]['y'] for key in lines_atas],
    #                         mode='lines',
    #                         name='Lines',
    #                         line=dict(color='blue', width=2))
    # lines_bawah_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_bawah],
    #                         y=[config_data[key]['y'] for key in lines_bawah],
    #                         mode='lines',
    #                         name='Lines',
    #                         line=dict(color='blue', width=2))
    # lines_tengah0_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_tengah0],
    #                         y=[config_data[key]['y'] for key in lines_tengah0],
    #                         mode='lines',
    #                         name='Lines',
    #                         line=dict(color='blue', width=2)) 
    # lines_tengah1_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_tengah1],
    #                         y=[config_data[key]['y'] for key in lines_tengah1],
    #                         mode='lines',
    #                         name='Lines',
    #                         line=dict(color='blue', width=2))

    # lines_tengah2_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_tengah2],
    #                         y=[config_data[key]['y'] for key in lines_tengah2],
    #                         mode='lines',
    #                         name='Lines',
    #                         line=dict(color='blue', width=2))


    

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

    # return {'data': [config_trace], 'layout': layout}


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