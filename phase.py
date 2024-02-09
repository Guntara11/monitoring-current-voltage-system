# import json
# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import plotly.graph_objs as go

# # Read configuration data from config.json
# with open('phase_to_phase.json') as config_file:
#     config_data = json.load(config_file)

# # Extract x and y coordinates and keys from config data
# config_keys = list(config_data.keys())
# config_x = [config_data[key]['x'] for key in config_data]
# config_y = [config_data[key]['y'] for key in config_data]

# # Initialize Dash app
# app = dash.Dash(__name__)

# # Layout of the dashboard
# app.layout = html.Div(
#     [
#         dcc.Graph(id='live-update-graph'),
#         dcc.Interval(
#             id='interval-component',
#             interval=1 * 200,  # in milliseconds
#             n_intervals=0
#         ),
#     ]
# )

# # Callback to update the graph
# @app.callback(Output('live-update-graph', 'figure'),
#               [Input('interval-component', 'n_intervals')])
# def update_graph(n):
#     # Scatter plot for config data
#     config_trace = go.Scatter(x=config_x, y=config_y,
#                               mode='markers',
#                               name='Config Points',
#                               marker=dict(color='red', size=10))

#     # Lines to connect specific points
#     lines_traces = []
#     for key, value in config_data.items():
#         if key.startswith("lines_"):
#             lines_trace = go.Scatter(x=[config_data[key]['x'], config_data[key[:-3]]['x']],
#                                      y=[config_data[key]['y'], config_data[key[:-3]]['y']],
#                                      mode='lines',
#                                      name='Lines',
#                                      line=dict(color='blue', width=2))
#             lines_traces.append(lines_trace)

#     # Connect each point with a line
#     connected_points = []
#     for i in range(len(config_x) - 1):
#         connected_points.append(go.Scatter(x=[config_x[i], config_x[i + 1]],
#                                            y=[config_y[i], config_y[i + 1]],
#                                            mode='lines',
#                                            line=dict(color='green', width=2)))

#     layout = go.Layout(title='Live Dashboard - Voltage vs Current with Config Points',
#                        xaxis=dict(title='Voltage'),
#                        yaxis=dict(title='Current'),
#                        showlegend=True,
#                        width=1400,
#                        height=800)

#     return {'data': [config_trace] + lines_traces + connected_points, 'layout': layout}

# # Run the app
# if __name__ == '__main__':
#     app.run_server(debug=True)

import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import deque
import paho.mqtt.client as mqtt

# MQTT Broker information
mqtt_broker = "broker.emqx.io"
mqtt_topic = "topic/sensor_data"

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div(
    [
        dcc.Graph(id='phase-to-phase-graph'),
        dcc.Graph(id='phase-to-gnd-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1 * 200,  # in milliseconds
            n_intervals=0
        ),
    ]
)

# Initialize data storage
mqtt_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)}

# Callback to update the graph for phase_to_phase
@app.callback(Output('phase-to-phase-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_phase_to_phase_graph(n):
    # Read configuration data from phase_to_phase.json
    with open('phase_to_phase.json') as config_file:
        config_data_phase_to_phase = json.load(config_file)

    # Scatter plot for MQTT data
    mqtt_trace = go.Scatter(x=list(mqtt_data['x']),
                            y=list(mqtt_data['y']),
                            mode='lines+markers',
                            name='Voltage vs Current')

    # Scatter plot for config data from phase_to_phase.json
    config_trace_phase_to_phase = go.Scatter(x=[config_data_phase_to_phase[key]['x'] for key in config_data_phase_to_phase],
                                              y=[config_data_phase_to_phase[key]['y'] for key in config_data_phase_to_phase],
                                              mode='markers',
                                              name='Config Points - Phase to Phase',
                                              marker=dict(color='red', size=10))

    # Lines to connect specific points
    lines_trace_phase_to_phase = go.Scatter(x=[config_data_phase_to_phase[key]['x'] for key in config_data_phase_to_phase],
                                            y=[config_data_phase_to_phase[key]['y'] for key in config_data_phase_to_phase],
                                            mode='lines',
                                            name='Lines - Phase to Phase',
                                            line=dict(color='blue', width=2))

    layout = go.Layout(title='Phase to Phase - Voltage vs Current with Config Points',
                       xaxis=dict(title='Voltage'),
                       yaxis=dict(title='Current'),
                       showlegend=True,
                       width=1400,
                       height=800)

    return {'data': [mqtt_trace, config_trace_phase_to_phase, lines_trace_phase_to_phase], 'layout': layout}

# Callback to update the graph for phase_to_gnd
@app.callback(Output('phase-to-gnd-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_phase_to_gnd_graph(n):
    # Read configuration data from phase_to_gnd.json
    with open('phase_to_gnd.json') as config_file:
        config_data_phase_to_gnd = json.load(config_file)

    # Scatter plot for MQTT data
    mqtt_trace = go.Scatter(x=list(mqtt_data['x']),
                            y=list(mqtt_data['y']),
                            mode='lines+markers',
                            name='Voltage vs Current')

    # Scatter plot for config data from phase_to_gnd.json
    config_trace_phase_to_gnd = go.Scatter(x=[config_data_phase_to_gnd[key]['x'] for key in config_data_phase_to_gnd],
                                           y=[config_data_phase_to_gnd[key]['y'] for key in config_data_phase_to_gnd],
                                           mode='markers',
                                           name='Config Points - Phase to Ground',
                                           marker=dict(color='blue', size=10))

    # Lines to connect specific points
    lines_trace_phase_to_gnd = go.Scatter(x=[config_data_phase_to_gnd[key]['x'] for key in config_data_phase_to_gnd],
                                          y=[config_data_phase_to_gnd[key]['y'] for key in config_data_phase_to_gnd],
                                          mode='lines',
                                          name='Lines - Phase to Ground',
                                          line=dict(color='green', width=2))

    layout = go.Layout(title='Phase to Ground - Voltage vs Current with Config Points',
                       xaxis=dict(title='Voltage'),
                       yaxis=dict(title='Current'),
                       showlegend=True,
                       width=1400,
                       height=800)

    return {'data': [mqtt_trace, config_trace_phase_to_gnd, lines_trace_phase_to_gnd], 'layout': layout}

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
