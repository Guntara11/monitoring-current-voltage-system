import random
import time
import coba_plotly
import csv
import os
from datetime import datetime
from pymongo import MongoClient
from utils import LineCalculation, MQTTClient

try:
    conn = MongoClient("mongodb://localhost:27017/")
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")

db = conn.MVCS
collection = db.Params

data_to_write = [] 
start_time = datetime.now()
data_to_write = {}

LINE_Mag_VI = []
LINE_Phase_Angles = []

LINE1_z0z1_mag = 6.181
LINE1_z0z1_ang = -2.55

def handle_Mag_data(data):
    LINE_Mag_VI.append(data)
    LINE_Mag_VI[:] = data

def handle_Phase_data(data):
    LINE_Phase_Angles.append(data)
    LINE_Phase_Angles[:] = data

def unpack_mag_data():
    if len(LINE_Mag_VI) == 0:
        return (0,) * 14 
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
        return (0,) * 6
    else:
        LINE1_Ang_U1 = 0
        LINE1_Ang_U2 = LINE_Phase_Angles[0]
        LINE1_Ang_U3 = LINE_Phase_Angles[1]
        LINE1_Ang_I1 = LINE_Phase_Angles[2]
        LINE1_Ang_I2 = LINE_Phase_Angles[3]
        LINE1_Ang_I3 = LINE_Phase_Angles[4]
        return LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3
    # return None

def process_data():
      global data_to_write
      global start_time

      LINE1_Freq, LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Uavg, LINE1_U12, LINE1_U23, LINE1_U31, LINE1_ULavg, LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_ILavg, LINE1_IN =  unpack_mag_data()
      LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3 = unpack_phase_data()
      line_calc = LineCalculation()
      
      try :
            line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                    LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                                    LINE1_z0z1_mag, LINE1_z0z1_ang)

            # Get real and imag  data
            IL1_Real, IL2_Real, IL3_Real, V1_Real, V2_Real, V3_Real = line_calc.get_real_data() 
            IL1_Imag, IL2_Imag, IL3_Imag, V1_Imag, V2_Imag, V3_Imag= line_calc.get_imag_data()
            IL1_Complex, IL2_Complex, IL3_Complex, V1_Complex, V2_Complex, V3_Complex = line_calc.get_complex_data()
            LINE1_IN_Real, LINE1_IN_Imag, LINE1_IN_Complex, LINE1_IN_Mag, LINE1_IN_Ang = line_calc.get_line1_IN_data()
            # k0 = line_calc.get_LINE1_k0()
            # n0 = line_calc.get_LINE1_n0()
            # product_result = line_calc.get_LINE1_PR()
            # LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()
            # LINE1_ZB_Real, LINE1_ZB_Imag, LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X = line_calc.get_ZB_data()
            # LINE1_ZC_Real, LINE1_ZC_Imag, LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X = line_calc.get_ZC_data()
            # LINE1_ZAB_Real, LINE1_ZAB_Imag, LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X = line_calc.get_ZAB_data()
            # LINE1_ZBC_Real, LINE1_ZBC_Imag, LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X = line_calc.get_ZBC_data()
            # LINE1_ZCA_Real, LINE1_ZCA_Imag, LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X = line_calc.get_ZCA_data()


            # # Printing data
            # print("IL1_Real:", IL1_Real)
            # print("IL2_Real:", IL2_Real)
            # print("IL3_Real:", IL3_Real)
            # print("V1_Real:", V1_Real)
            # print("V2_Real:", V2_Real)
            # print("V3_Real:", V3_Real)

            # print("IL1_Imag = {0}\nIL2_Imag = {1}\nIL3_Imag = {2}".format(IL1_Imag, IL2_Imag, IL3_Imag))

            # print("V1_Imag = {0}\nV2_Imag = {1}\nV3_Imag = {2}".format(V1_Imag, V2_Imag, V3_Imag))

            # print("IL1_Complex = {0}\nIL2_Complex = {1}\nIL3_Complex = {2}".format(IL1_Complex, IL2_Complex, IL3_Complex))

            # print("V1_Complex = {0}\nV2_Complex = {1}\nV3_Complex = {2}".format(V1_Complex, V2_Complex, V3_Complex))

            # print("LINE1_IN_Complex = {0}\nLINE1_IN_Imag = {1}\nLiNE1_IN_Real = {2}\nLINE1_IN_Mag{3}\nLiNE1_IN_Ang".format(LINE1_IN_Complex, LINE1_IN_Imag, LINE1_IN_Real, LINE1_IN_Mag, LINE1_IN_Ang))

            # print("k0 = {0}\nn0 = {1}\nproduct result = {2}".format(k0, n0, product_result))

            # print("LINE1_ZA_Real = {0}\nLINE1_ZA_Imag = {1}\nLINE1_ZA_Mag = {2}\nLINE1_ZA_Ang = {3}\nLINE1_ZA_R = {4}\nLINE1_ZA_X = {5}"
            #       .format(LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X))  

            # # print("LINE1_ZB_data", zb_data)
            # print("LINE1_ZB_Real = {0}\nLINE1_ZB_Imag = {1}\nLINE1_ZB_Mag = {2}\nLINE1_ZB_Ang = {3}\nLINE1_ZB_R = {4}\nLINE1_ZB_X = {5}"
            #       .format(LINE1_ZB_Real, LINE1_ZB_Imag, LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X))

            # print("LINE1_ZC_Real = {0}\nLINE1_ZC_Imag = {1}\nLINE1_ZC_Mag = {2}\nLINE1_ZC_Ang = {3}\nLINE1_ZC_R = {4}\nLINE1_ZC_X = {5}"
            #       .format(LINE1_ZC_Real, LINE1_ZC_Imag, LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X))

            # print("LINE1_ZAB_Mag = {0}\nLINE1_ZAB_Ang = {1}\nLINE1_ZAB_R = {2}\nLINE1_ZAB_X = {3}".format(LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X))

            # print("LINE1_ZBC_Mag = {0}\nLINE1_ZBC_Ang = {1}\nLINE1_ZBC_R = {2}\nLINE1_ZBC_X = {3}".format(LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X))

            # print("LINE1_ZCA_Mag = {0}\nLINE1_ZCA_Ang = {1}\nLINE1_ZCA_R = {2}\nLINE1_ZCA_X = {3}".format(LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X))
            # time.sleep(10)
            data_to_write = {
                        'Timestamp' : datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                        'DATE' : datetime.now().strftime("%Y-%m-%d"), 'TIME' : datetime.now().strftime("%H:%M:%S"),
                        'LINE_IL1' : LINE1_IL1, 'LINE_IL1-Ang' : LINE1_Ang_I1, 
                        'LINE_IL2' : LINE1_IL2, 'LINE_IL2-Ang' : LINE1_Ang_I2,
                        'LINE_IL3' : LINE1_IL3, 'LINE_IL3-Ang' : LINE1_Ang_I3,
                        'LINE_UL1' : LINE1_U1, 'LINE_UL1-Ang' : LINE1_Ang_U1,
                        'LINE_UL2' : LINE1_U2, 'LINE_UL2-Ang' : LINE1_Ang_U2,
                        'LINE_UL3' : LINE1_U3, 'LINE_UL3-Ang' : LINE1_Ang_U3,
                        'LINE1_z0z1_mag' : LINE1_z0z1_mag, 'LINE1_z0z1_ang':LINE1_z0z1_ang,
                        'LINE1_IL1_Real' : str(IL1_Real), 'LINE1_IL2_Real' : str(IL2_Real), 'LINE1_IL3_Real' : str(IL3_Real),
                        'LINE1_IL1_Imag' : str(IL1_Imag), 'LINE1_IL2_Imag' : str(IL2_Imag), 'LINE1_IL3_Imag' : str(IL3_Imag),
                        'LINE1_V1_Real' : str(V1_Real), 'LINE1_V2_Real' : str(V2_Real), 'LINE1_V3_Real' : str(V3_Real),
                        'LINE1_V1_Imag' : str(V1_Imag), 'LINE1_V2_Imag' : str(V2_Imag), 'LINE1_V3_Imag' : str(V3_Imag),
                        'LINE1_IL1_Complex' : str(IL1_Complex), 'LINE1_IL2_Complex' : str(IL2_Complex), 'LINE1_IL3_Complex' : str(IL3_Complex),
                        'LINE1_V1_Complex' : str(V1_Complex), 'LINE1_V2_Complex' : str(V2_Complex), 'LINE1_V3_Complex' : str(V3_Complex),
                        'LINE1_IN_Imag' : str(LINE1_IN_Imag), 'LINE1_IN_Real' : str(LINE1_IN_Real), 'LINE1_IN_Mag' : str(LINE1_IN_Mag), 'LINE1_IN_Ang' : str(LINE1_IN_Ang) 
                  }
            # Store Data to MongoDB
            collection.insert_one(data_to_write)
            time.sleep(1)

            # # Generate File CSV 
            # generate_csv(data_to_write)
            

            # elapsed_time = datetime.now() - start_time
            # if elapsed_time.total_seconds() >= 600:
            #     # Write data to CSV
            #     generate_csv(data_to_write)
            #     print("Data written to CSV.")
            #     # Reset data and start time
            #     data_to_write = {}
            #     start_time = datetime.now()
                
      except ZeroDivisionError :
           pass

def run_mqtt_data_retrieval():
    mqtt_client = MQTTClient(on_data_callback=handle_Mag_data)
    mqtt_client.set_mqtt_topic1("data/sensor1")  # Set MQTT topic 1
    mqtt_client.connect()

def run_mqtt_angle_retreival():
    mqtt_client = MQTTClient(on_data_callback=handle_Phase_data)
    mqtt_client.set_mqtt_topic2("data/sensor2")  # Set MQTT topic 1
    mqtt_client.connect()

# def generate_csv(data):
#     global data_to_write
#     global start_time

#     csv_file_path = 'data_csv'  # Folder to store CSV files
#     if not os.path.exists(csv_file_path):
#         os.makedirs(csv_file_path)

#     current_file_time = start_time.strftime("%Y%m%d_%H%M%S")
#     filename = f"{csv_file_path}/{current_file_time}.csv"
#     file_exists = os.path.exists(filename)
#     with open(filename, mode='a', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=data.keys())
#         if not file_exists:
#             writer.writeheader()
#         writer.writerow(data)
#         time.sleep(0.2)
           
            
if __name__ == '__main__':
    while True:
        run_mqtt_data_retrieval()
        run_mqtt_angle_retreival()
        process_data()