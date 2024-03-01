# import random
# import time
# import json
# import csv
# import paho.mqtt.client as mqtt

# mqtt_broker = "broker.emqx.io"  # Ganti dengan alamat broker MQTT Anda
# mqtt_port = 1883
# mqtt_topic = "topic/sensor_data"
# mqtt_topic2 = "topic/dummy_impendance"

# client = mqtt.Client()

# def on_connect(client, userdata, flags, rc):
#     print("Connected to MQTT Broker with result code " + str(rc))

# client.on_connect = on_connect
# client.connect(mqtt_broker, mqtt_port, 60)

# impedance = {"x": 10, 
#             "y": 20}
# client.publish(mqtt_topic2, json.dumps(impedance))

# csv_file_path = "sensor_data.csv"
# max_data_entries = 50
# data_buffer = []

# while True:
#     data = {"voltage": round(random.uniform(-10, 10), 2), 
#             "current": round(random.uniform(-10, 10), 2)}
    
#     client.publish(mqtt_topic, json.dumps(data))
    
#     if len(data_buffer) < max_data_entries:
#         data_buffer.append(data)
#     else:
#         data_buffer.pop(0)  # Remove the oldest entry
#         data_buffer.append(data)
    
#     with open(csv_file_path, mode='w', newline='') as csv_file:
#         fieldnames = ['timestamp', 'voltage', 'current']
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         writer.writeheader()
        
#         for i, entry in enumerate(data_buffer):
#             timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#             data_to_write = {'timestamp': timestamp, 'voltage': entry['voltage'], 'current': entry['current']}
#             writer.writerow(data_to_write)
    
#     print(f"Random data: {data}")
#     time.sleep(0.2)

import paho.mqtt.client as mqtt
import json

class MQTTClient:
    def __init__(self, on_data_callback):
        self.mqtt_broker = "broker.emqx.io"
        self.mqtt_port = 1883
        self.mqtt_topic = "data/sensor"
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.on_data_callback = on_data_callback

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT Broker with result code " + str(rc))
        client.subscribe(self.mqtt_topic)

    def on_message(self, client, userdata, msg):
        if msg.topic == self.mqtt_topic:
            data = json.loads(msg.payload)
            self.on_data_callback(data)

    def connect(self):
        self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.client.loop_forever()  # Start a blocking loop to handle MQTT messages