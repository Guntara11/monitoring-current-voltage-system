import random
import time
from pymongo import MongoClient

try:
    conn = MongoClient("mongodb+srv://sopian23:Sopian010799@cluster0.kzuf6tu.mongodb.net/")
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")

db = conn.DataRandom
collection = db.MyCollect

while True:
    data = {
        "voltage": random.randint(1, 100),
        "current" : random.randint(1, 100)
    }

    # Insert new data into the collection
    collection.insert_one(data)
    print("data:", data)

    time.sleep(5)  # Wait for 5 seconds before inserting the next data
