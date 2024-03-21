import random
import time
from pymongo import MongoClient

# Flask imports
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

try:
    conn = MongoClient("mongodb+srv://guntara11:Assalaam254@cluster0.zqxli6w.mongodb.net/")
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")

db = conn.myDB
collection = db.MyCollection

document_limit = 50

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    send_data()

def send_data():
    while True:
        data = {
            "voltage": round(random.uniform(-10, 10), 2), 
            "current": round(random.uniform(-10, 10), 2)
        }

        # Check the count of documents/data
        count = collection.count_documents({})

        if count < document_limit:
            # insert data
            collection.insert_one(data)
            print("data:", data)
            socketio.emit('update', data)
            time.sleep(0.2)
        else:
            # If the count is 5 or more, update each document one by one in sequence
            oldest_documents = collection.find({}).sort("_id", 1).limit(document_limit)

            for doc in oldest_documents:
                # Update the values of each document
                updated_data = {
                    "$set": {
                        "voltage": random.randint(1, 100),
                        "current": random.randint(1, 100),
                    }
                }
                collection.update_one({"_id": doc["_id"]}, updated_data)
                print("Update data:", doc["_id"], "with data:", updated_data)
                socketio.emit('update', updated_data)
                time.sleep(0.2)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)