import random
import time
import utils
from utils import LineCalculation
import csv
import os
from datetime import datetime
from pymongo import MongoClient

try:
    conn = MongoClient("mongodb+srv://guntara11:Assalaam254@cluster0.zqxli6w.mongodb.net/")
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")

db = conn.MVCS
collection = db.Params

data_to_write = []  # Data to be written to CSV
start_time = datetime.now()  # Start time for CSV file

def generate_csv(data) :
      global data_to_write
      global start_time
      
      csv_file_path = 'data_csv'  # Folder to store CSV files
      if not os.path.exists(csv_file_path):
            os.makedirs(csv_file_path)

      # current_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
      current_file_time = start_time.strftime("%Y%m%d_%H%M%S")
      filename = f"{csv_file_path}/{current_file_time}.csv"
      # Check if the CSV file exists, if not, create it and write the header
      file_exists = os.path.exists(filename)
      with open(filename, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            # Write the header only if the file doesn't exist
            if not file_exists:
                  writer.writeheader()
            writer.writerow(data)
            
def main() :
      global data_to_write
      global start_time

      while True:

            # LINE1_U1 = 89236.961
            # LINE1_U2 = 89521.813
            # LINE1_U3 = 89844.727
            # LINE1_Ang_U1 = 117.274
            # LINE1_Ang_U2 = 356.92
            # LINE1_Ang_U3 = 237.173

            # LINE1_IL1 = 86.126
            # LINE1_IL2 = 87.365
            # LINE1_IL3 = 100.566
            # LINE1_Ang_I1 = 112.977
            # LINE1_Ang_I2 = 0.044
            # LINE1_Ang_I3 = 232.82

            # LINE1_z0z1_mag = 6.181
            # LINE1_z0z1_ang = -2.55
            # Create LineCalculation object and pass random values
            line_calc = LineCalculation()
            line_calc.calculate_values(utils.LINE1_U1, utils.LINE1_U2, utils.LINE1_U3, utils.LINE1_Ang_U1, utils.LINE1_Ang_U2, utils.LINE1_Ang_U3,
                                          utils.LINE1_IL1, utils.LINE1_IL2, utils.LINE1_IL3, utils.LINE1_Ang_I1, utils.LINE1_Ang_I2, utils.LINE1_Ang_I3,
                                          utils.LINE1_z0z1_mag, utils.LINE1_z0z1_ang)

            # Get real and imag  data
            IL1_Real, IL2_Real, IL3_Real, V1_Real, V2_Real, V3_Real = line_calc.get_real_data() 
            IL1_Imag, IL2_Imag, IL3_Imag, V1_Imag, V2_Imag, V3_Imag= line_calc.get_imag_data()
            IL1_Complex, IL2_Complex, IL3_Complex, V1_Complex, V2_Complex, V3_Complex = line_calc.get_complex_data()
            LINE1_IN_Real, LINE1_IN_Imag, LINE1_IN_Complex, LINE1_IN_Mag, LINE1_IN_Ang = line_calc.get_line1_IN_data()
            k0 = line_calc.get_LINE1_k0()
            n0 = line_calc.get_LINE1_n0()
            product_result = line_calc.get_LINE1_PR()
            LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = line_calc.get_ZA_data()
            LINE1_ZB_Real, LINE1_ZB_Imag, LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X = line_calc.get_ZB_data()
            LINE1_ZC_Real, LINE1_ZC_Imag, LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X = line_calc.get_ZC_data()
            LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X = line_calc.get_ZAB_data()
            LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X = line_calc.get_ZBC_data()
            LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X = line_calc.get_ZCA_data() 


            # Printing data
            print("IL1_Real:", IL1_Real)
            print("IL2_Real:", IL2_Real)
            print("IL3_Real:", IL3_Real)
            print("V1_Real:", V1_Real)
            print("V2_Real:", V2_Real)
            print("V3_Real:", V3_Real)
            
            print("IL1_Imag = {0}\nIL2_Imag = {1}\nIL3_Imag = {2}".format(IL1_Imag, IL2_Imag, IL3_Imag))
            
            print("V1_Imag = {0}\nV2_Imag = {1}\nV3_Imag = {2}".format(V1_Imag, V2_Imag, V3_Imag))
            
            print("IL1_Complex = {0}\nIL2_Complex = {1}\nIL3_Complex = {2}".format(IL1_Complex, IL2_Complex, IL3_Complex))
            
            print("V1_Complex = {0}\nV2_Complex = {1}\nV3_Complex = {2}".format(V1_Complex, V2_Complex, V3_Complex))
            
            print("LINE1_IN_Complex = {0}\nLINE1_IN_Imag = {1}\nLiNE1_IN_Real = {2}\nLINE1_IN_Mag{3}\nLiNE1_IN_Ang".format(LINE1_IN_Complex, LINE1_IN_Imag, LINE1_IN_Real, LINE1_IN_Mag, LINE1_IN_Ang))
            
            print("k0 = {0}\nn0 = {1}\nproduct result = {2}".format(k0, n0, product_result))
            
            print("LINE1_ZA_Real = {0}\nLINE1_ZA_Imag = {1}\nLINE1_ZA_Mag = {2}\nLINE1_ZA_Ang = {3}\nLINE1_ZA_R = {4}\nLINE1_ZA_X = {5}"
                  .format(LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X))  
            
            # print("LINE1_ZB_data", zb_data)
            print("LINE1_ZB_Real = {0}\nLINE1_ZB_Imag = {1}\nLINE1_ZB_Mag = {2}\nLINE1_ZB_Ang = {3}\nLINE1_ZB_R = {4}\nLINE1_ZB_X = {5}"
                  .format(LINE1_ZB_Real, LINE1_ZB_Imag, LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X))
            
            print("LINE1_ZC_Real = {0}\nLINE1_ZC_Imag = {1}\nLINE1_ZC_Mag = {2}\nLINE1_ZC_Ang = {3}\nLINE1_ZC_R = {4}\nLINE1_ZC_X = {5}"
                  .format(LINE1_ZC_Real, LINE1_ZC_Imag, LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X))
            
            print("LINE1_ZAB_Mag = {0}\nLINE1_ZAB_Ang = {1}\nLINE1_ZAB_R = {2}\nLINE1_ZAB_X = {3}".format(LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X))

            print("LINE1_ZBC_Mag = {0}\nLINE1_ZBC_Ang = {1}\nLINE1_ZBC_R = {2}\nLINE1_ZBC_X = {3}".format(LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X))
   
            print("LINE1_ZCA_Mag = {0}\nLINE1_ZCA_Ang = {1}\nLINE1_ZCA_R = {2}\nLINE1_ZCA_X = {3}".format(LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X))
            time.sleep(10)
            data_to_write = {
                    'Timestamp' : datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                    'DATE' : datetime.now().strftime("%Y-%m-%d"), 'TIME' : datetime.now().strftime("%H:%M:%S"),
                    'LINE_IL1' : utils.LINE1_IL1, 'LINE_IL1-Ang' : utils.LINE1_Ang_I1, 
                    'LINE_IL2' : utils.LINE1_IL2, 'LINE_IL2-Ang' : utils.LINE1_Ang_I2,
                    'LINE_IL3' : utils.LINE1_IL3, 'LINE_IL3-Ang' : utils.LINE1_Ang_I3,
                    'LINE_UL1' : utils.LINE1_U1, 'LINE_UL1-Ang' : utils.LINE1_Ang_U1,
                    'LINE_UL2' : utils.LINE1_U2, 'LINE_UL2-Ang' : utils.LINE1_Ang_U2,
                    'LINE_UL3' : utils.LINE1_U3, 'LINE_UL3-Ang' : utils.LINE1_Ang_U3,
                    'LINE1_z0z1_mag' : utils.LINE1_z0z1_mag, 'LINE1_z0z1_ang':utils.LINE1_z0z1_ang,
                    'LINE1_IL1_Real' : str(IL1_Real), 'LINE1_IL2_Real' : str(IL2_Real), 'LINE1_IL3_Real' : str(IL3_Real),
                    'LINE1_IL1_Imag' : str(IL1_Imag), 'LINE1_IL2_Imag' : str(IL2_Imag), 'LINE1_IL3_Imag' : str(IL3_Imag),
                    'LINE1_V1_Real' : str(V1_Real), 'LINE1_V2_Real' : str(V2_Real), 'LINE1_V3_Real' : str(V3_Real),
                    'LINE1_V1_Imag' : str(V1_Imag), 'LINE1_V2_Imag' : str(V2_Imag), 'LINE1_V3_Imag' : str(V2_Imag),
                    'LINE1_IL1_Complex' : str(IL1_Complex), 'LINE1_IL2_Complex' : str(IL2_Complex), 'LINE1_IL3_Complex' : str(IL3_Complex),
                    'LINE1_V1_Complex' : str(V1_Complex), 'LINE1_V2_Complex' : str(V2_Complex), 'LINE1_V3_Complex' : str(V3_Complex),
                    'LINE1_IN_Imag' : str(LINE1_IN_Imag), 'LINE1_IN_Real' : str(LINE1_IN_Real), 'LINE1_IN_Mag' : str(LINE1_IN_Mag), 'LINE1_IN_Ang' : str(LINE1_IN_Ang) 
                }

            # Store Data to MongoDB
            collection.insert_one(data_to_write)
            time.sleep(0.2)
            # Generate File CSV 
            generate_csv(data_to_write)

            elapsed_time = datetime.now() - start_time
            if elapsed_time.total_seconds() >= 600:
                # Write data to CSV
                generate_csv(data_to_write)
                print("Data written to CSV.")
                # Reset data and start time
                data_to_write = {}
                start_time = datetime.now()
            
            

if __name__ == '__main__':
      main()