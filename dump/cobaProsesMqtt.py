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

LINE1_z0z1_mag = 6.181
LINE1_z0z1_ang = -2.55



ZA_Real = []
ZA_Imag = []


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


def unpack_mag_data():
    if len(LINE_Mag_VI) == 0:
        return (0,) * 14  # Return a tuple of 14 zeros if LINE_Phase_Angles is empty
    else:
        LINE1_Freq = LINE_Mag_VI[0]
        LINE1_U1 = LINE_Mag_VI[1]
        LINE1_U2 = LINE_Mag_VI[2]
        LINE1_U3 = LINE_Mag_VI[3]
        LINE1_Uavg = LINE_Mag_VI[4]
        LINE1_U12 = LINE_Mag_VI[5]
        LINE1_U23 = LINE_Mag_VI[6]
        LINE1_U31 = LINE_Mag_VI[7]
        LINE1_ULavg = LINE_Mag_VI[8]
        LINE1_IL1 = LINE_Mag_VI[9]
        LINE1_IL2 = LINE_Mag_VI[10]
        LINE1_IL3 = LINE_Mag_VI[11]
        LINE1_ILavg = LINE_Mag_VI[12]
        LINE1_IN = LINE_Mag_VI[13]
        return LINE1_Freq, LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Uavg, LINE1_U12, LINE1_U23, LINE1_U31, LINE1_ULavg, LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_ILavg, LINE1_IN
    # return None


def unpack_phase_data():
    if len(LINE_Phase_Angles) == 0:
        return (0,) * 6  # Return a tuple of 14 zeros if LINE_Phase_Angles is empty
    else:
        LINE1_Ang_U1 = 0
        LINE1_Ang_U2 = LINE_Phase_Angles[0]
        LINE1_Ang_U3 = LINE_Phase_Angles[1]
        LINE1_Ang_I1 = LINE_Phase_Angles[2]
        LINE1_Ang_I2 = LINE_Phase_Angles[3]
        LINE1_Ang_I3 = LINE_Phase_Angles[4]
        return LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3
    # return None

def unpack_Iharm_data():
    if len(LINE_I_Harm) == 0:
        return (0,) * 6  # Return a tuple of 14 zeros if LINE_Phase_Angles is empty
    else:
        LINE1_IA3rd_Harm = LINE_I_Harm[0]
        LINE1_IA5th_Harm = LINE_I_Harm[1]
        LINE1_IB3rd_Harm = LINE_I_Harm[2]
        LINE1_IB5th_Harm = LINE_I_Harm[3]
        LINE1_IC3rd_Harm = LINE_I_Harm[4]
        LINE1_IC5th_Harm = LINE_I_Harm[5]
        
        return  LINE1_IA3rd_Harm, LINE1_IA5th_Harm, LINE1_IB3rd_Harm, LINE1_IB5th_Harm, LINE1_IC3rd_Harm, LINE1_IC5th_Harm
    # return None

def unpack_Vharm_data():
    if len(LINE_V_Harm) == 0:
        return (0,) * 6  # Return a tuple of 14 zeros if LINE_Phase_Angles is empty
    else:
        LINE1_VA3rd_Harm = LINE_V_Harm[0]
        LINE1_VA5th_Harm = LINE_V_Harm[1]
        LINE1_VB3rd_Harm = LINE_V_Harm[2]
        LINE1_VB5th_Harm = LINE_V_Harm[3]
        LINE1_VC3rd_Harm = LINE_V_Harm[4]
        LINE1_VC5th_Harm = LINE_V_Harm[5]
        
        return  LINE1_VA3rd_Harm, LINE1_VA5th_Harm, LINE1_VB3rd_Harm, LINE1_VB5th_Harm, LINE1_VC3rd_Harm, LINE1_VC5th_Harm
    # return None


def process_data():
    
    LINE1_Freq, LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Uavg, LINE1_U12, LINE1_U23, LINE1_U31, LINE1_ULavg, LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_ILavg, LINE1_IN =  unpack_mag_data()
    LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3 = unpack_phase_data()
    LINE1_IA3rd_Harm, LINE1_IA5th_Harm, LINE1_IB3rd_Harm, LINE1_IB5th_Harm, LINE1_IC3rd_Harm, LINE1_IC5th_Harm = unpack_Iharm_data()
    LINE1_VA3rd_Harm, LINE1_VA5th_Harm, LINE1_VB3rd_Harm, LINE1_VB5th_Harm, LINE1_VC3rd_Harm, LINE1_VC5th_Harm = unpack_Vharm_data()
    VAB = LINE1_U12 
    VBC = LINE1_U12
    VA = LINE1_U1
    IA = LINE1_IL1  
    IA_ang = LINE1_Ang_I1
    line_calc = LineCalculation()
    
    try :
        line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                    LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                                    LINE1_z0z1_mag, LINE1_z0z1_ang)
        LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()

        ZA_Real.append(LINE1_ZA_Real)
        ZA_Imag.append(LINE1_ZA_Imag)
        if len(ZA_Real) >= 2:
            ZA_Real.pop(0)
        if len(ZA_Imag) >=2:
            ZA_Imag.pop(0)

    except ZeroDivisionError:
        pass

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
    while True:
        run_mqtt_data_retrieval()
        line_data = unpack_mag_data()
        run_mqtt_angle_retreival()
        phasedata = unpack_phase_data()
        run_mqtt_Vharm_retreival()
        Vharm_data = unpack_Vharm_data()
        run_mqtt_Iharm_retreival() 
        Iharm_data = unpack_Iharm_data()
        # process_data()
        print("line_data", line_data)
        # print("ZA_Real:", ZA_Real)
        # print("ZA_Imag:", ZA_Imag)
        print("phasedata :", phasedata)
        print("Vharm data :", Vharm_data)
        print("Iharm data :", Iharm_data)