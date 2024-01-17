import pymongo
import time 
from plyer import notification

# Replace these values with your MongoDB connection details
mongo_uri = "mongodb+srv://guntara11:Assalaam254@cluster0.zqxli6w.mongodb.net/myDB"
collection_name = "MyCollection"

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
while True:
    # Query to retrieve all documents in the collection
    query = {}

    # Retrieve data from MongoDB
    cursor = collection.find(query)

    # Print the retrieved data
    print("Data from MongoDB:")
    for document in cursor:
        print(document)
        time.sleep(0.2) 

    # Close the MongoDB connection
    # interval_seconds = 1  # Adjust this value as needed
    # time.sleep(interval_seconds)