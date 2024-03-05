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


def process_Mag_data():
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


        return LINE2_Freq, LINE2_U1, LINE2_U2, LINE2_U3, LINE2_Uavg, LINE2_U12, LINE2_U23, LINE2_U31, LINE2_ULavg, LINE2_IL1, LINE2_IL2, LINE2_IL3, LINE2_ILavg, LINE2_IN
    return None

def process_Phase_data():
    if len(LINE_Phase_Angles) == 0:
        pass
    else:
        LINE2_Ang_U2 = LINE_Phase_Angles[0]
        LINE2_Ang_U3 = LINE_Phase_Angles[1]
        LINE2_Ang_I1 = LINE_Phase_Angles[2]
        LINE2_Ang_I2 = LINE_Phase_Angles[3]
        LINE2_Ang_I3 = LINE_Phase_Angles[4]

        return  LINE2_Ang_U2, LINE2_Ang_U3, LINE2_Ang_I1, LINE2_Ang_I2, LINE2_Ang_I3
    return None

def process_Vharm_data():
    if len(LINE_V_Harm) == 0:
        pass
    else:
        LINE2_VA3rd_Harm = LINE_V_Harm[0]
        LINE2_VA5th_Harm = LINE_V_Harm[1]
        LINE2_VB3rd_Harm = LINE_V_Harm[2]
        LINE2_VB5th_Harm = LINE_V_Harm[3]
        LINE2_VC3rd_Harm = LINE_V_Harm[4]
        LINE2_VC5th_Harm = LINE_V_Harm[5]
        
        return  LINE2_VA3rd_Harm, LINE2_VA5th_Harm, LINE2_VB3rd_Harm, LINE2_VB5th_Harm, LINE2_VC3rd_Harm, LINE2_VC5th_Harm
    return None

def process_Iharm_data():
    if len(LINE_I_Harm) == 0:
        pass
    else:
        LINE2_IA3rd_Harm = LINE_I_Harm[0]
        LINE2_IA5th_Harm = LINE_I_Harm[1]
        LINE2_IB3rd_Harm = LINE_I_Harm[2]
        LINE2_IB5th_Harm = LINE_I_Harm[3]
        LINE2_IC3rd_Harm = LINE_I_Harm[4]
        LINE2_IC5th_Harm = LINE_I_Harm[5]
        
        return  LINE2_IA3rd_Harm, LINE2_IA5th_Harm, LINE2_IB3rd_Harm, LINE2_IB5th_Harm, LINE2_IC3rd_Harm, LINE2_IC5th_Harm
    return None

def ZA_data(mag_data):
    if mag_data:
        LINE1_U1 = mag_data[1]
        LINE1_U2 = mag_data[2]
        LINE1_U3 = mag_data[3]
        LINE1_Ang_U1 = mag_data[0]
        LINE1_Ang_U2 = mag_data[4]
        LINE1_Ang_U3 = mag_data[5]
        LINE1_IL1 = mag_data[9]
        LINE1_IL2 = mag_data[10]
        LINE1_IL3 = mag_data[11]
        LINE1_Ang_I1 = mag_data[6]
        LINE1_Ang_I2 = mag_data[7]
        LINE1_Ang_I3 = mag_data[8]
        LINE1_z0z1_mag = mag_data[12]
        LINE1_z0z1_ang = mag_data[13]

        line_calc = LineCalculation()
        line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                    LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                                    LINE1_z0z1_mag, LINE1_z0z1_ang)
        LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()

        ZA_Real.append(LINE1_ZA_Real)
        ZA_Imag.append(LINE1_ZA_Imag)
        if len(ZA_Real) >= 51:
            ZA_Real.pop(0)
        if len(ZA_Imag) >= 51:
            ZA_Imag.pop(0)

        print("ZA Real :", ZA_Real)
        print("ZA Imag :", ZA_Imag)

        return ZA_Real, ZA_Imag
    
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

def main():
    while True:
        mag_data = process_Mag_data()
        phase_data = process_Phase_data()
        vharm_data = process_Vharm_data()
        iharm_data = process_Iharm_data()
        ZA_data(mag_data)
        time.sleep(0.4)
    
    # if phase_data:
    #     print("\nPhase Data:")
    #     print("LINE2_Ang_U2:", phase_data[0])
    #     print("LINE2_Ang_U3:", phase_data[1])
    #     print("LINE2_Ang_I1:", phase_data[2])
    #     print("LINE2_Ang_I2:", phase_data[3])
    #     print("LINE2_Ang_I3:", phase_data[4])

    # if vharm_data:
    #     print("\nVoltage Harmonic Data:")
    #     print("LINE2_VA3rd_Harm:", vharm_data[0])
    #     print("LINE2_VA5th_Harm:", vharm_data[1])
    #     print("LINE2_VB3rd_Harm:", vharm_data[2])
    #     print("LINE2_VB5th_Harm:", vharm_data[3])
    #     print("LINE2_VC3rd_Harm:", vharm_data[4])
    #     print("LINE2_VC5th_Harm:", vharm_data[5])

    # if iharm_data:
    #     print("\nCurrent Harmonic Data:")
    #     print("LINE2_IA3rd_Harm:", iharm_data[0])
    #     print("LINE2_IA5th_Harm:", iharm_data[1])
    #     print("LINE2_IB3rd_Harm:", iharm_data[2])
    #     print("LINE2_IB5th_Harm:", iharm_data[3])
    #     print("LINE2_IC3rd_Harm:", iharm_data[4])
    #     print("LINE2_IC5th_Harm:", iharm_data[5])

if __name__ == "__main__":
    # freq = process_Mag_data()
    while True:
        run_mqtt_data_retrieval()
        run_mqtt_angle_retreival()
        run_mqtt_Vharm_retreival()
        run_mqtt_Iharm_retreival()
        main()
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
        time.sleep(0.4)