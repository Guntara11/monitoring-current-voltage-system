import dash
from dash import html, dcc, Input, Output, State, dash_table
import pandas as pd
import pymongo

# Ganti URL koneksi dengan URL koneksi MongoDB Atlas Anda
client = pymongo.MongoClient("mongodb+srv://sopiand23:Manusiakuat1@mycluster.bfapaaq.mongodb.net/")
db = client["MyData"]
collection = db["MyCollect"]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1('Web Application connected to a Live Database', style={'textAlign': 'center'}),
    dcc.Interval(id='interval_db', interval=86400000, n_intervals=0),  # Set interval to 1 day (86400000 milliseconds)
    html.Div([
        dcc.Input(id='start-time', type='text', placeholder='Start Timestamp (YYYY-MM-DD_HH:MM:SS)'),
        dcc.Input(id='end-time', type='text', placeholder='End Timestamp (YYYY-MM-DD_HH:MM:SS)'),
        html.Button('Filter Data', id='filter-button', n_clicks=0)
    ]),
    html.Div(id='mongo-datatable', children=[]),
])

# Callback to fetch and display filtered data
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
            ),
        ]
    else:
        return []

if __name__ == '__main__':
    app.run_server(debug=True)
