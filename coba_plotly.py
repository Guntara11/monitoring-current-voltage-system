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

# Ganti URL koneksi dengan URL koneksi MongoDB Atlas Anda
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["MVCS"]
collection = db["Params"]

config_folder = 'config_imp'
config_files = [os.path.join(config_folder, f) for f in os.listdir(config_folder) if f.endswith('.json')]

# Initialize Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR], suppress_callback_exceptions=True)


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
            id="config-dropdown",
            options=[{'label': f'Line {i+1}', 'value': f'line{i+1}.json'} for i, f in enumerate(config_files)],
            value=config_files[0] if config_files else None,
            clearable=False,
        ),
    ],
    className="mb-4",
)

filter_start_input = dbc.Row([
    html.Label("End Timestamp (YYYY-MM-DD_HH:MM:SS)", style={'color': 'white'}),
    html.Div(
    [
        dbc.Input(type="Timestamp", id="start_time", placeholder="Start Time"),
        dbc.Label("Enter Start Time"),
    ]),
    ],
    className="mb-3"
)
filter_end_input = dbc.Row([
        html.Label("End Timestamp (YYYY-MM-DD_HH:MM:SS)", style={'color': 'white'}),
        html.Div([
        dbc.Input(type="Timestamp", id="end_time", placeholder="End Time"),
        dbc.Label("Enter End Time")
    ]),

    ],
    className="mb-3",
)

button = html.Div(
    [
        dbc.Button("FIlter Data", color="secondary", className="me-1",  n_clicks=0),
        dbc.Button("Save CSV", color="secondary", className="me-1",  n_clicks=0)
    ],
    className="d-grid gap-2",
)

filter_time = dbc.Form([filter_start_input, filter_end_input])

control1 = dbc.Card(
    [dropdown, filter_time, button],
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
                                            ],  width=20),
                                            dbc.Col([
                                                control1,
                                                # ************************************
                                                # Uncomment line below when running locally!
                                                # ************************************
                                                # theme_controls
                                            ],  width=20),
                                        ]),
                                # Display warning message if no configuration file is selected
                                html.Div(id='warning-message', children=[]),

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
    
ZA_data = []

@app.callback(
    [Output('phase-to-gnd-graph', 'figure'),
     Output('phase-to-phase-graph', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('config-dropdown', 'value')])

def update_graphs(n, selected_config):
    if not selected_config:
        return {}, {}

    # Path file konfigurasi
    config_file_path = os.path.join('config_imp', selected_config)

    # Periksa apakah file konfigurasi ada
    if not os.path.exists(config_file_path):
        return {
            'data': [],
            'layout': {
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
            }
        }, {
            'data': [],
            'layout': {
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
            }
        }

    # Jika file konfigurasi ada, lanjutkan proses membaca dan memperbarui grafik
    with open(config_file_path, 'r') as config_file:
        config_data = json.load(config_file)

    # Ambil nilai dari file JSON
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

    return fig_phase_to_gnd, fig_phase_to_phase

# Callback to save filtered data to CSV
@app.callback(
    Output('save-csv-message', 'children'),
    [Input('save-csv-button', 'n_clicks')],
    [State('start-time', 'value'),
     State('end-time', 'value')]
)
def save_filtered_data_to_csv(n_clicks, start_time, end_time):
    if n_clicks > 0 and start_time and end_time:
        # Fetch data from MongoDB within the specified timestamp range
        filtered_data = collection.find({"Timestamp": {"$gte": start_time, "$lte": end_time}})
        
        # Convert the fetched data to a DataFrame
        df = pd.DataFrame(list(filtered_data))
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"filter_data_{timestamp}.csv"
        
        # Define the directory to save CSV files
        save_folder = 'data_csv'
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        
        # Save the DataFrame to CSV
        csv_path = os.path.join(save_folder, filename)
        df.to_csv(csv_path, index=False)
        
        return html.Div(f"Data filtered successfully saved to {csv_path}", style={'color': 'green'})

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