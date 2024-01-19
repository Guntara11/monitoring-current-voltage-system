import pymongo
from plyer import notification
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash import dash_table
import plotly.express as px
# Replace these values with your MongoDB connection details
mongo_uri = "mongodb+srv://sopian23:Sopian010799@cluster0.kzuf6tu.mongodb.net/DataRandom"
collection_name = "MyCollect"

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)

# Access the specified database and collection
db = client.get_database()
collection = db[collection_name]

# Notify when connected to the database
notification.notify(
    title="Script Connected to MongoDB",
    message="The script has successfully connected to the MongoDB database.",
)

# Retrieve data from MongoDB
def get_data():
    query = {}
    cursor = collection.find(query)
    data_list = [document for document in cursor]
    return data_list

# Create Dash app
app = dash.Dash(__name__)

# Layout of the web dashboard
app.layout = html.Div([
    html.H1("MongoDB Data Dashboard"),
    dcc.Graph(id='scatter-plot'),
    dash_table.DataTable(
        id='data-table',
        columns=[
            {'name': 'Voltage', 'id': 'voltage'},
            {'name': 'Current', 'id': 'current'}
        ],
        style_table={'height': '300px', 'overflowY': 'auto'},
    ),
    dcc.Interval(
        id='interval-component',
        interval=1*200,  # Change the interval to 1 second (in milliseconds)
        n_intervals=0
    )
])

# Callback to update the scatter plot
@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('data-table', 'data')],
    Input('interval-component', 'n_intervals')
)
def update_scatter_plot(n):
    data = get_data()

    if not data:
          return (px.scatter(x=[], y=[], labels={'x': 'Voltage', 'y': 'Current'}),
                [])
    
    # Extract 'voltage' and 'current' data from each document
    voltage_values = [doc['voltage'] for doc in data]
    current_values = [doc['current'] for doc in data]
    # Assuming data contains fields 'x' and 'y'
    # Create a scatter plot
    fig = px.scatter(
        x=voltage_values,
        y=current_values,
        labels={'x': 'Voltage', 'y': 'Current'},
        title='Scatter Plot'
    )
    table_data = [{'voltage': voltage, 'current': current} for voltage, current in zip(voltage_values, current_values)]
    return (fig, table_data)


if __name__ == '__main__':
    app.run_server(debug=True)
