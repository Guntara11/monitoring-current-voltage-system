import utils
from utils import LineCalculation, MQTTClient
import time


ZA_Real = []
ZA_Imag = []

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

        # Perform calculations using LineCalculation class
    line_calc = LineCalculation()
    calculated_values = line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                                LINE1_z0z1_mag, LINE1_z0z1_ang)
    
    LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()
    # print("LINE1_ZA_Real = {0}\nLINE1_ZA_Imag = {1}"
    #               .format(LINE1_ZA_Real, LINE1_ZA_Imag)) 
    ZA_Real.append(LINE1_ZA_Real)
    ZA_Imag.append(LINE1_ZA_Imag)
    if len(ZA_Real) >= 2:
        ZA_Real.pop(0)
    if len(ZA_Imag) >=2:
        ZA_Imag.pop(0)

def run_mqtt_data_retrieval():
    mqtt_client = MQTTClient(on_data_callback=handle_mqtt_data)
    mqtt_client.connect()

if __name__ == "__main__":
    
    while True:
        run_mqtt_data_retrieval()
        print("ZA_real", ZA_Real)
        print("ZA_Imag", ZA_Imag)
        time.sleep(1)