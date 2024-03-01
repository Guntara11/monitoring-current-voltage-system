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

mqtt_broker = "broker.emqx.io"  # Sesuaikan dengan broker MQTT yang Anda gunakan
mqtt_port = 1883
mqtt_topic = "data/sensor"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    if msg.topic == mqtt_topic:
        data = json.loads(msg.payload)
        params(data)

def params(data):
    LINE1_U1 = data[1]
    LINE1_U2 = data[2]
    LINE1_U3 = data[3]
    # LINE1_Ang_U1 = data[3]
    # LINE1_Ang_U2 = data[4]
    # LINE1_Ang_U3 = data[5]
    LINE1_IL1 = data[9]
    LINE1_IL2 = data[10]
    LINE1_IL3 = data[11]
    # LINE1_Ang_I1 = data[9]
    # LINE1_Ang_I2 = data[10]
    # LINE1_Ang_I3 = data[11]
    # LINE1_z0z1_mag = data[12]
    # LINE1_z0z1_ang = data[13]

    
    print(f"LINE1_U1: {LINE1_U1}")
    print(f"LINE1_U2: {LINE1_U2}")
    print(f"LINE1_U3: {LINE1_U3}")
    # print(f"LINE1_Ang_U1: {LINE1_Ang_U1}")
    # print(f"LINE1_Ang_U2: {LINE1_Ang_U2}")
    # print(f"LINE1_Ang_U3: {LINE1_Ang_U3}")
    print(f"LINE1_IL1: {LINE1_IL1}")
    print(f"LINE1_IL2: {LINE1_IL2}")
    print(f"LINE1_IL3: {LINE1_IL3}")
    # print(f"LINE1_Ang_I1: {LINE1_Ang_I1}")
    # print(f"LINE1_Ang_I2: {LINE1_Ang_I2}")
    # print(f"LINE1_Ang_I3: {LINE1_Ang_I3}")
    # print(f"LINE1_z0z1_mag: {LINE1_z0z1_mag}")
    # print(f"LINE1_z0z1_ang: {LINE1_z0z1_ang}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)

client.loop_forever()