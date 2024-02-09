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

lines_kanan = ["kanan_bawah_z1","kanan_samping_z1", "kanan_samping_z2", "kanan_samping_z3"]
lines_kiri = ["kiri_atas_z3","kiri_samping_z1", "kiri_samping_z2", "kiri_samping_z3"]
lines_atas = ["kiri_atas_z3", "reach_z3", "kanan_samping_z3"]
lines_bawah = ["kiri_bawah_z1", "point", "kanan_bawah_z1"]
lines_tengah0 = ["point", "reach_z1", "reach_z2", "reach_z3"]
lines_tengah1=["kiri_atas_z1", "reach_z1", "kanan_atas_z1"]
lines_tengah2=["kiri_atas_z2", "reach_z2", "kanan_samping_z2"]

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
# Layout of the dashboard
app.layout = html.Div(
    [
        html.Label('Select Config File:'),
        dcc.Dropdown(
            id='config-dropdown',
            options=[{'label': f, 'value': f} for f in config_files],
            value=config_files[0] if config_files else None
        ),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000,  # in milliseconds
            n_intervals=0
        ),
    ]
)
# Initialize data storage
mqtt_data = {'x': deque(maxlen=50), 'y': deque(maxlen=50)}

# Callback to update the graph
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('config-dropdown', 'value')])




def update_graph(n, selected_config):
    if not selected_config:
        return {}

    # Read configuration data from the selected config file
    with open(selected_config) as config_file:
        config_data = json.load(config_file)

    config_keys = list(config_data.keys())
    config_x = [config_data[key]['x'] for key in config_data]
    config_y = [config_data[key]['y'] for key in config_data]

    # Scatter plot for MQTT data
    mqtt_trace = go.Scatter(x=list(mqtt_data['x']),
                            y=list(mqtt_data['y']),
                            mode='lines+markers',
                            name='Voltage vs Current')

    # Scatter plot for config data
    config_trace = go.Scatter(x=config_x, y=config_y,
                              mode='markers',
                              name='Config Points',
                              marker=dict(color='red', size=10))
    
 # Add text annotations for config points
    annotations = [dict(x=x, y=y, text=key, showarrow=True, arrowhead=2, arrowcolor='black', arrowsize=1)
                   for key, x, y in zip(config_keys, config_x, config_y)]
    
    # Lines to connect specific points
    lines_kanan_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_kanan],
                            y=[config_data[key]['y'] for key in lines_kanan],
                            mode='lines',
                            name='Lines',
                            line=dict(color='blue', width=2))
    lines_kiri_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_kiri],
                            y=[config_data[key]['y'] for key in lines_kiri],
                            mode='lines',
                            name='Lines',
                            line=dict(color='blue', width=2))
    lines_atas_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_atas],
                            y=[config_data[key]['y'] for key in lines_atas],
                            mode='lines',
                            name='Lines',
                            line=dict(color='blue', width=2))
    lines_bawah_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_bawah],
                            y=[config_data[key]['y'] for key in lines_bawah],
                            mode='lines',
                            name='Lines',
                            line=dict(color='blue', width=2))
    lines_tengah0_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_tengah0],
                            y=[config_data[key]['y'] for key in lines_tengah0],
                            mode='lines',
                            name='Lines',
                            line=dict(color='blue', width=2)) 
    lines_tengah1_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_tengah1],
                            y=[config_data[key]['y'] for key in lines_tengah1],
                            mode='lines',
                            name='Lines',
                            line=dict(color='blue', width=2))

    lines_tengah2_trace = go.Scatter(x=[config_data[key]['x'] for key in lines_tengah2],
                            y=[config_data[key]['y'] for key in lines_tengah2],
                            mode='lines',
                            name='Lines',
                            line=dict(color='blue', width=2))

    layout = go.Layout(title='Live Dashboard - Voltage vs Current with Config Points',
                       xaxis=dict(title='Voltage'),
                       yaxis=dict(title='Current'),
                       showlegend=True,
                        width=1400,
                       height=800)

    return {'data': [mqtt_trace, config_trace, lines_kanan_trace, lines_kiri_trace, lines_atas_trace, lines_bawah_trace,
                     lines_tengah0_trace, lines_tengah1_trace, lines_tengah2_trace], 'layout': layout}
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