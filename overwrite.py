# import random
# import time
# from pymongo import MongoClient

# try: 
#     conn = MongoClient("mongodb+srv://sopian23:Sopian010799@cluster0.kzuf6tu.mongodb.net/") 
#     print("Connected successfully!!!") 
# except:   
#     print("Could not connect to MongoDB")

# db = conn.DataRandom
# collection = db.MyCollect

# while True:
#     data = {
#         "random_number": random.randint(1, 100),
#         # Add more fields as needed
#     }

#     # Insert new data
#     collection.insert_one(data)
#     print("data:", data)

#     # Check the count of documents in the collection
#     current_count = collection.count_documents({})
#     time.sleep(5)

#     # If the count exceeds 5, remove the oldest document
#     if current_count > 5:
#         oldest_document = collection.find_one_and_delete({}, sort=[('_id', 1)])
#         print("Removed oldest document:", oldest_document)

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

document_limit = 5

while True:
    data = {
        "voltage": random.randint(1, 100),
        "current" : random.randint(1, 100),
    }

    # Check the count of documents/data
    count = collection.count_documents({})

    if count < document_limit:
        #insert data
        collection.insert_one(data)
        print("data:", data)
        time.sleep(5)
    else:
        # If the count is 5 or more, update each document one by one in sequence
        oldest_documents = collection.find({}).sort("_id", 1).limit(document_limit)

        for doc in oldest_documents:
            # Update the values of each document
            updated_data = {
                "$set": {
                    "voltage": random.randint(1, 100),
                    "current" : random.randint(1, 100),
                }
            }
            collection.update_one({"_id": doc["_id"]}, updated_data)
            print("Update data:", doc["_id"], "with data:", updated_data)
            time.sleep(5)