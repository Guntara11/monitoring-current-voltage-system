import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from cobaProsesMqtt import mqtt_data
import time


while True:
    print(mqtt_data)
    time.sleep(1)
# app = dash.Dash(__name__)

# # Define Dash layout
# app.layout = html.Div([
#     dcc.Graph(id='live-graph'),
#     dcc.Interval(
#         id='graph-update',
#         interval=1000,  # Update every 1 second
#         n_intervals=0
#     )
# ])

# @app.callback(Output('live-graph', 'figure'),
#               [Input('graph-update', 'n_intervals')])
# def update_graph(n):
#     # Extract data from the shared variable for plotting
#     # For example, assuming the MQTT data has two values (x, y)
#     x_data = [data[0] for data in mqtt_data]
#     y_data = [data[1] for data in mqtt_data]

#     # Plot the data
#     trace = go.Scatter(
#         x=x_data,
#         y=y_data,
#         mode='lines',
#         name='Data'
#     )

#     layout = go.Layout(title='MQTT Data')

#     return {'data': [trace], 'layout': layout}

# if __name__ == '__main__':
#     app.run_server(debug=True)