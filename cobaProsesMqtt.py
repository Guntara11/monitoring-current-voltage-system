from mqtt_Client import MQTTClient

def handle_mqtt_data(data):
    # Process the received data here
    LINE1_U1 = data[1]
    LINE1_U2 = data[2]
    LINE1_U3 = data[3]
    LINE1_Ang_U1 = data[0]
    LINE1_Ang_U2 = data[4]
    LINE1_Ang_U3 = data[5]
    LINE1_IL1 = data[9]
    LINE1_IL2 = data[10]
    LINE1_IL3 = data[11]
    LINE1_Ang_I1 = data[6]
    LINE1_Ang_I2 = data[7]
    LINE1_Ang_I3 = data[8]
    LINE1_z0z1_mag = data[12]
    LINE1_z0z1_ang = data[13]

    print(f"LINE1_U1: {LINE1_U1}")
    print(f"LINE1_U2: {LINE1_U2}")
    print(f"LINE1_U3: {LINE1_U3}")
    print(f"LINE1_Ang_U1: {LINE1_Ang_U1}")
    print(f"LINE1_Ang_U2: {LINE1_Ang_U2}")
    print(f"LINE1_Ang_U3: {LINE1_Ang_U3}")
    print(f"LINE1_IL1: {LINE1_IL1}")
    print(f"LINE1_IL2: {LINE1_IL2}")
    print(f"LINE1_IL3: {LINE1_IL3}")
    print(f"LINE1_Ang_I1: {LINE1_Ang_I1}")
    print(f"LINE1_Ang_I2: {LINE1_Ang_I2}")
    print(f"LINE1_Ang_I3: {LINE1_Ang_I3}")
    print(f"LINE1_z0z1_mag: {LINE1_z0z1_mag}")
    print(f"LINE1_z0z1_ang: {LINE1_z0z1_ang}")


if __name__ == "__main__":
    mqtt_client = MQTTClient(on_data_callback=handle_mqtt_data)
    mqtt_client.connect()