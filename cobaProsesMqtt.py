import utils
from utils import LineCalculation, MQTTClient
import time
import math 
import cmath
import struct



LINE_Mag_VI = []
LINE_Phase_Angles = []
LINE_V_Harm = []
LINE_I_Harm = []





ZA_Real = []
ZA_Imag = []
IA_data= []
IA_data_ang= []
IB_data= []
IB_data_ang= []
IC_data= []
IC_data_ang= []

VA_data= []
VA_data_ang= []
VB_data= []
VB_data_ang= []
VC_data= []
VC_data_ang= []

def handle_Mag_data(data):
    LINE_Mag_VI.append(data)
    LINE_Mag_VI[:] = data

def handle_Phase_data(data):
    LINE_Phase_Angles.append(data)
    LINE_Phase_Angles[:] = data

def handle_Vharm_data(data):
    LINE_V_Harm.append(data)
    LINE_V_Harm[:] = data

def handle_Iharm_data(data):
    LINE_I_Harm.append(data)
    LINE_I_Harm[:] = data

<<<<<<< Updated upstream
    return {'data': [trace], 'layout': layout}



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

        # Perform calculations using LineCalculation class
    line_calc = LineCalculation()
    calculated_values = line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                                LINE1_z0z1_mag, LINE1_z0z1_ang)
=======
def process_data():
    if len(LINE_Mag_VI) == 0:
        pass
    else:
        LINE2_Freq = LINE_Mag_VI[0]
        LINE2_U1 = LINE_Mag_VI[1]
        LINE2_U2 = LINE_Mag_VI[2]
        LINE2_U3 = LINE_Mag_VI[3]
        LINE2_Uavg = LINE_Mag_VI[4]
        LINE2_U12 = LINE_Mag_VI[5]
        LINE2_U23 = LINE_Mag_VI[6]
        LINE2_U31 = LINE_Mag_VI[7]
        LINE2_ULavg = LINE_Mag_VI[8]
        LINE2_IL1 = LINE_Mag_VI[9]
        LINE2_IL2 = LINE_Mag_VI[10]
        LINE2_IL3 = LINE_Mag_VI[11]
        LINE2_ILavg = LINE_Mag_VI[12]
        LINE2_IN = LINE_Mag_VI[13]
>>>>>>> Stashed changes
    
    return LINE2_Freq
# def handle_ang_data(data):
#     LINE2_Ang_U2 = data[0]
#     LINE2_Ang_U3 = data[1]
#     LINE2_Ang_I1 = data[2]
#     LINE2_Ang_I2 = data[3]
#     LINE2_Ang_I3 = data[4]
#     print(data)


# def handle_ang_data(data):
#     LINE2_Ang_U2 = data[0]
#     LINE2_Ang_U3 = data[1]
#     LINE2_Ang_I1 = data[2]
#     LINE2_Ang_I2 = data[3]
#     LINE2_Ang_I3 = data[4]
#     print(data)


def run_mqtt_data_retrieval():
    mqtt_client = MQTTClient(on_data_callback=handle_Mag_data)
    mqtt_client.set_mqtt_topic1("data/sensor1")  # Set MQTT topic 1
    mqtt_client.connect()




def run_mqtt_angle_retreival():
    mqtt_client = MQTTClient(on_data_callback=handle_Phase_data)
    mqtt_client.set_mqtt_topic2("data/sensor2")  # Set MQTT topic 1
    mqtt_client.connect()

def run_mqtt_Vharm_retreival():

    mqtt_client = MQTTClient(on_data_callback=handle_Vharm_data)
    mqtt_client.set_mqtt_topic2("data/sensor3")  # Set MQTT topic 1
    mqtt_client.connect()

def run_mqtt_Iharm_retreival():

    mqtt_client = MQTTClient(on_data_callback=handle_Iharm_data)
    mqtt_client.set_mqtt_topic2("data/sensor4")  # Set MQTT topic 1
    mqtt_client.connect()



if __name__ == "__main__":
    freq = process_data()
    while True:
        run_mqtt_data_retrieval()
        run_mqtt_angle_retreival()
        run_mqtt_Vharm_retreival()
        run_mqtt_Iharm_retreival()
        print("MAG DATA", LINE_Mag_VI)
        print("FREQ DATA", freq)
        print("PHASE DATA", LINE_Phase_Angles)
        print("Vharm DATA", LINE_V_Harm)
        print("Iharm DATA", LINE_I_Harm)
        # print("ZA_real", ZA_Real)
        # print("ZA_Imag", ZA_Imag)
        # print("IA_data", IA_data)
        # print("IA_data_ang", IA_data_ang)
        # print("IB_data", IB_data)
        # print("IB_data_ang", IB_data_ang)
        # print("IC_data", IC_data)
        # print("IC_data_ang", IC_data_ang)

        # print("VA_data", VA_data)
        # print("VA_data_ang", VA_data_ang)
        # print("VB_data", VB_data)
        # print("VB_data_ang", VB_data_ang)
        # print("VC_data", VC_data)
        # print("VC_data_ang", VC_data_ang)
        # time.sleep(0.4)