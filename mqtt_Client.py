import random
import time
import json
import paho.mqtt.client as mqtt

mqtt_broker = "broker.emqx.io"  # Ganti dengan alamat broker MQTT Anda
mqtt_port = 1883
mqtt_topic = "topic/sensor_data"

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))

client.on_connect = on_connect
client.connect(mqtt_broker, mqtt_port, 60)

while True:
    data = {"voltage": random.randint(1, 100), 
            "current": random.randint(1, 100)}
    
    client.publish(mqtt_topic, json.dumps(data))
    
    print(f"Random data: {data}")
    time.sleep(0.2)