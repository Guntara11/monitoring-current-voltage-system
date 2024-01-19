import streamlit as st
import pymongo
import pandas as pd




# Replace these values with your MongoDB connection details
mongo_uri = "mongodb+srv://sopiand23:Manusiakuat1@mycluster.bfapaaq.mongodb.net/DataRandom"
collection_name = "MyCollect"

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)

# Access the specified database and collection
db = client.get_database()
collection = db[collection_name]


# Retrieve data from MongoDB
def get_data():
    query = {}
    cursor = collection.find(query)
    data_list = [document for document in cursor]
    return data_list

# Streamlit app
st.title("MongoDB Data Visualization")

# Display raw data
st.subheader("Raw Data:")
raw_data = get_data()
st.write(pd.DataFrame(raw_data))

# Scatter plot
st.subheader("Scatter Plot:")
scatter_df = pd.DataFrame(raw_data)
scatter_plot = st.scatter_chart(scatter_df, x='voltage', y='current')

# Update the data every 1 second
while True:
    scatter_df = pd.DataFrame(get_data())
    scatter_plot.scatter_chart(scatter_df, x='voltage', y='current')

# streamlit run plot_streamlit.py