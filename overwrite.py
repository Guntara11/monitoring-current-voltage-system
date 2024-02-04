import random
import time
import pytz
from pymongo import MongoClient
from datetime import datetime

try:
    conn = MongoClient("mongodb+srv://guntara11:Assalaam254@cluster0.zqxli6w.mongodb.net/")
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")

db = conn.myDB
collection = db.MyCollection
document_limit = 50
utc_plus_7 = pytz.timezone('Asia/Bangkok')
while True:
    data = {
        "timestamp": datetime.now(utc_plus_7),
        "voltage": random.randint(1, 100),
        "current" : random.randint(1, 100),
    }

    # Check the count of documents/data
    count = collection.count_documents({})

    if count < document_limit:
        #insert data
        collection.insert_one(data)
        print("data:", data)
        time.sleep(0.2)
    else:
        # If the count is 5 or more, update each document one by one in sequence
        oldest_documents = collection.find({}).sort("_id", 1).limit(document_limit)

        for doc in oldest_documents:
            # Update the values of each document
            updated_data = {
                "$set": {
                    "timestamp": datetime.now(utc_plus_7),
                    "voltage": random.randint(1, 100),
                    "current" : random.randint(1, 100),
                }
            }
            collection.update_one({"_id": doc["_id"]}, updated_data)
            print("Update data:", doc["_id"], "with data:", updated_data)
            time.sleep(0.2)
