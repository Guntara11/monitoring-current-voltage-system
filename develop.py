import asyncio
import time
import math
import cmath
import struct
from pymodbus.client import ModbusSerialClient
from aiogram import Bot, Dispatcher
import random
import csv
import os
from datetime import datetime

# Replace 'YOUR_BOT_TOKEN' with the actual token you received from BotFather
bot_token = '6723591840:AAFgHD2wJOd0kNYSdkr8g-OrOBUwnJORZ1U'

# Initialize the bot and dispatcher
bot = Bot(token=bot_token)
dp = Dispatcher()

# Replace 'CHAT_ID' with the chat ID of the user or group you want to send the message to
chat_id = -4120767546  # Example chat ID

cooldown_period = 5  # Cooldown period in seconds

async def send_telegram_message(message_text):
    await bot.send_message(chat_id, message_text)

data_to_write = []  # Data to be written to CSV
start_time = datetime.now()  # Start time for CSV file

async def generate_csv(data):
    global data_to_write
    global start_time

    csv_file_path = 'data_csv'  # Folder to store CSV files
    if not os.path.exists(csv_file_path):
        os.makedirs(csv_file_path)

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

# async def new_generate_csv(data):
#     global data_to_write
#     global start_time

#     csv_file_path = 'data_csv'  # Folder to store CSV files
#     if not os.path.exists(csv_file_path):
#         os.makedirs(csv_file_path)

#     current_file_time = start_time.strftime("%Y%m%d_%H%M%S")
#     filename = f"{csv_file_path}/{current_file_time}.csv"

#     # Check if the CSV file exists, if not, create it and write the header
#     file_exists = os.path.exists(filename)
#     with open(filename, mode='a', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=data.keys())
#         # Write the header only if the file doesn't exist
#         if not file_exists:
#             writer.writeheader()
#         writer.writerow(data)

async def main_async():
    # Set up Modbus serial connection for LINE1
    #client1 = ModbusSerialClient(method='rtu', port='COM9', baudrate=19200, stopbits=1, bytesize=8, parity='N')
    global data_to_write
    global start_time
    # Function to read and format float registers
    def read_float_registers(client, start_address, num_registers, unit):
        data = []
        for i in range(num_registers):
            response = client.read_holding_registers(start_address + i * 2, 2, unit=unit)
            if not response.isError():
                int_value = (response.registers[0] << 16) | response.registers[1]
                float_value = struct.unpack('f', struct.pack('I', int_value))[0]
                data.append(float_value)
            else:
                data.append(0.0)  # Handle error condition
        return data
            
    while True: 
        LINE1_Arr = []


        # Define LINE_NAME
        LINE1_NAME = 'CEMPAKA-KANDANGAN'
        
        # Define LINE1_SETPOINT_IN and LINE2_SETPOINT_IN
        LINE1_SETPOINT_IN = 22
        
        # Define LINE1_IN_NL NORMAL LOAD
        LINE1_IN_NL = 10
        
            # Define LINE1_IN_PL PEAK LOAD
        LINE1_IN_PL = 20
        
        # Initialize the last_warning_time for both LINE1 and LINE2
        last_warning_time_LINE1 = 0
        
    
          
        while True:  # Infinite loop
            ###########################
            # Add code for LINE1 data reading and processing here
            ###########################
            #User
            #fill in the variable with this number, so we can simulate to calculate

            # Generate random values in main.py
            LINE1_U1 = random.uniform(80000, 90000)
            LINE1_U2 = random.uniform(80000, 90000)
            LINE1_U3 = random.uniform(80000, 90000)
            LINE1_Ang_U1 = random.uniform(0, 360)
            LINE1_Ang_U2 = random.uniform(0, 360)
            LINE1_Ang_U3 = random.uniform(0, 360)

            LINE1_IL1 = random.uniform(80, 120)
            LINE1_IL2 = random.uniform(80, 120)
            LINE1_IL3 = random.uniform(80, 120)
            LINE1_Ang_I1 = random.uniform(0, 360)
            LINE1_Ang_I2 = random.uniform(0, 360)
            LINE1_Ang_I3 = random.uniform(0, 360)

            LINE1_z0z1_mag = 6.181
            LINE1_z0z1_ang = -2.55
            
            # Calculate IL1_Real using the formula
            LINE1_IL1_Real = LINE1_IL1 * math.cos(math.radians(LINE1_Ang_I1))
            LINE1_IL2_Real = LINE1_IL2 * math.cos(math.radians(LINE1_Ang_I2))
            LINE1_IL3_Real = LINE1_IL3 * math.cos(math.radians(LINE1_Ang_I3))
            LINE1_Arr.extend([LINE1_IL1_Real, LINE1_IL2_Real, LINE1_IL3_Real])
            
            # Calculate IL1_Imag using the formula (LINE1_IL1 * SIN(LINE1_Ang_I1 * PI() / 180))
            LINE1_IL1_Imag = LINE1_IL1 * math.sin(math.radians(LINE1_Ang_I1))
            LINE1_IL2_Imag = LINE1_IL2 * math.sin(math.radians(LINE1_Ang_I2))
            LINE1_IL3_Imag = LINE1_IL3 * math.sin(math.radians(LINE1_Ang_I3))
            LINE1_Arr.extend([LINE1_IL1_Imag, LINE1_IL2_Imag, LINE1_IL3_Imag])
            
            # Calculate V1_Real, V2_Real, and V3_Real (assuming LINE1_U1, LINE1_U2, and LINE1_U3 are phase voltages)
            LINE1_V1_Real = LINE1_U1 * math.cos(math.radians(LINE1_Ang_U1))
            LINE1_V2_Real = LINE1_U2 * math.cos(math.radians(LINE1_Ang_U2))
            LINE1_V3_Real = LINE1_U3 * math.cos(math.radians(LINE1_Ang_U3))
            LINE1_Arr.extend([LINE1_V1_Real, LINE1_V2_Real, LINE1_V3_Real])
            
            LINE1_V1_Imag = LINE1_U1 * math.sin(math.radians(LINE1_Ang_U1))
            LINE1_V2_Imag = LINE1_U2 * math.sin(math.radians(LINE1_Ang_U2))
            LINE1_V3_Imag = LINE1_U3 * math.sin(math.radians(LINE1_Ang_U3))
            LINE1_Arr.extend([LINE1_V1_Imag, LINE1_V2_Imag, LINE1_V3_Imag])
            
            # Create complex numbers for LINE1_V2_Complex, LINE1_V3_Complex, LINE1_IL1_Complex, LINE1_IL2_Complex, and LINE1_IL3_Complex
            LINE1_IL1_Complex = complex(LINE1_IL1_Real, LINE1_IL1_Imag)
            LINE1_IL2_Complex = complex(LINE1_IL2_Real, LINE1_IL2_Imag)
            LINE1_IL3_Complex = complex(LINE1_IL3_Real, LINE1_IL3_Imag)
            LINE1_V1_Complex = complex(LINE1_V1_Real, LINE1_V1_Imag)
            LINE1_V2_Complex = complex(LINE1_V2_Real, LINE1_V2_Imag)
            LINE1_V3_Complex = complex(LINE1_V3_Real, LINE1_V3_Imag)
            LINE1_Arr.extend([LINE1_IL1_Complex, LINE1_IL2_Complex, LINE1_IL3_Complex, LINE1_V1_Complex, LINE1_V2_Complex, LINE1_V3_Complex])
            
            # Create LINE1_IL_Real and LINE1_IL_Imag arrays
            LINE1_IL_Real = [LINE1_IL1_Real, LINE1_IL2_Real, LINE1_IL3_Real]
            LINE1_IL_Imag = [LINE1_IL1_Imag, LINE1_IL2_Imag, LINE1_IL3_Imag]
            LINE1_IL_Complex = [LINE1_IL1_Complex, LINE1_IL2_Complex, LINE1_IL3_Complex]
            
            
            # Create LINE1_V_Real and LINE1_V_Imag arrays
            LINE1_V_Real = [LINE1_V1_Real, LINE1_V2_Real, LINE1_V3_Real]
            LINE1_V_Imag = [LINE1_V1_Imag, LINE1_V2_Imag, LINE1_V3_Imag]
            LINE1_V_Complex = [LINE1_V1_Complex, LINE1_V2_Complex, LINE1_V3_Complex]
            
            
            # Calculate LINE1_IN_Complex as the sum of LINE1_IL1_Complex, LINE1_IL2_Complex, and LINE1_IL3_Complex
            LINE1_IN_Complex = -24.3725335851725-2.63909674692661j



            # Calculate LINE1_IN_Imag and LINE1_IN_Real
            LINE1_IN_Imag = LINE1_IN_Complex.imag
            LINE1_IN_Real = LINE1_IN_Complex.real

            # Calculate LINE1_IN_Mag
            LINE1_IN_Mag = math.sqrt(LINE1_IN_Real**2 + LINE1_IN_Imag**2)

            # Calculate LINE1_IN_Ang
            LINE1_IN_Ang = math.degrees(math.atan2(LINE1_IN_Imag, LINE1_IN_Real))
            LINE1_Arr.extend([LINE1_IN_Mag, LINE1_IN_Ang, LINE1_IN_Real, LINE1_IN_Imag, LINE1_IN_Complex])
            
            # Add the calculated variables to the array
            LINE1_V_Arr = [LINE1_V_Real, LINE1_V_Imag]
            LINE1_I_Arr = [LINE1_IL_Real, LINE1_IL_Imag]
            LINE1_IN_Arr = [LINE1_IN_Mag, LINE1_IN_Ang, LINE1_IN_Real, LINE1_IN_Imag, LINE1_IN_Complex]
            

            # Calculate LINE1_ZA_Mag, Ang, R, X
            
            LINE1_z0z1_ang_rad = math.radians(LINE1_z0z1_ang)
            LINE1_k0 = cmath.rect(LINE1_z0z1_mag, LINE1_z0z1_ang_rad) - 1
            LINE1_complex_number = complex(3, 0)
            LINE1_n0 = LINE1_k0 / LINE1_complex_number

            product_result = LINE1_IN_Complex * LINE1_n0
            sum_result = LINE1_IL1_Complex + product_result
            LINE1_ZA = LINE1_V1_Complex / sum_result

            LINE1_ZA_Real = LINE1_ZA.real
            LINE1_ZA_Imag = LINE1_ZA.imag
            LINE1_Arr.extend([LINE1_ZA_Real, LINE1_ZA_Imag])


            LINE1_ZA_Mag = abs(LINE1_V1_Complex / LINE1_IL1_Complex)
            LINE1_ZA_Ang = math.degrees(cmath.phase(LINE1_V1_Complex / LINE1_IL1_Complex))					
            LINE1_ZA_Ang_radians = math.radians(LINE1_ZA_Ang)
            LINE1_ZA_R = LINE1_ZA_Mag * math.cos(LINE1_ZA_Ang_radians)
            LINE1_ZA_X = LINE1_ZA_Mag * math.sin(LINE1_ZA_Ang_radians)
            LINE1_Arr.extend([LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X])
            

            
            
            # Calculate LINE1_ZB_Mag, Ang, R, X
            
            LINE1_z0z1_ang_rad = math.radians(LINE1_z0z1_ang)
            LINE1_k0 = cmath.rect(LINE1_z0z1_mag, LINE1_z0z1_ang_rad) - 1
            LINE1_complex_number = complex(3, 0)
            LINE1_n0 = LINE1_k0 / LINE1_complex_number

            product_result = LINE1_IN_Complex * LINE1_n0
            sum_result = LINE1_IL2_Complex + product_result
            LINE1_ZB = LINE1_V2_Complex / sum_result

            LINE1_ZB_Real = LINE1_ZB.real
            LINE1_ZB_Imag = LINE1_ZB.imag
            LINE1_Arr.extend([LINE1_ZB_Real, LINE1_ZB_Imag])


            LINE1_ZB_Mag = abs(LINE1_V2_Complex / LINE1_IL2_Complex)
            LINE1_ZB_Ang = math.degrees(cmath.phase(LINE1_V2_Complex / LINE1_IL2_Complex))					
            LINE1_ZB_Ang_radians = math.radians(LINE1_ZB_Ang)
            LINE1_ZB_R = LINE1_ZB_Mag * math.cos(LINE1_ZB_Ang_radians)
            LINE1_ZB_X = LINE1_ZB_Mag * math.sin(LINE1_ZB_Ang_radians)
            LINE1_Arr.extend([LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X])
            
            # Calculate LINE1_ZC_Mag, Ang, R, X
            
            LINE1_z0z1_ang_rad = math.radians(LINE1_z0z1_ang)
            LINE1_k0 = cmath.rect(LINE1_z0z1_mag, LINE1_z0z1_ang_rad) - 1
            LINE1_complex_number = complex(3, 0)
            LINE1_n0 = LINE1_k0 / LINE1_complex_number

            product_result = LINE1_IN_Complex * LINE1_n0
            sum_result = LINE1_IL3_Complex + product_result
            LINE1_ZC = LINE1_V3_Complex / sum_result

            LINE1_ZC_Real = LINE1_ZC.real
            LINE1_ZC_Imag = LINE1_ZC.imag
            LINE1_Arr.extend([LINE1_ZC_Real, LINE1_ZC_Imag])


            LINE1_ZC_Mag = abs(LINE1_V3_Complex / LINE1_IL3_Complex)
            LINE1_ZC_Ang = math.degrees(cmath.phase(LINE1_V3_Complex / LINE1_IL3_Complex))					
            LINE1_ZC_Ang_radians = math.radians(LINE1_ZC_Ang)
            LINE1_ZC_R = LINE1_ZC_Mag * math.cos(LINE1_ZC_Ang_radians)
            LINE1_ZC_X = LINE1_ZC_Mag * math.sin(LINE1_ZC_Ang_radians)
            LINE1_Arr.extend([LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X])

                                
            # Calculate LINE1_ZAB_Mag, Ang, R, X




            
            LINE1_ZAB_Mag = abs((LINE1_V1_Complex - LINE1_V2_Complex) / (LINE1_IL1_Complex - LINE1_IL2_Complex))
            LINE1_diff_V1_V2 = LINE1_V1_Complex - LINE1_V2_Complex
            LINE1_diff_IL1_IL2 = LINE1_IL1_Complex - LINE1_IL2_Complex
            LINE1_ZAB_Ang = math.degrees(math.atan2(LINE1_diff_V1_V2.imag, LINE1_diff_V1_V2.real) - math.atan2(LINE1_diff_IL1_IL2.imag, LINE1_diff_IL1_IL2.real))
            LINE1_ZAB_Ang_radians = math.radians(LINE1_ZAB_Ang)
            LINE1_ZAB_R = LINE1_ZAB_Mag * math.cos(LINE1_ZAB_Ang_radians)
            LINE1_ZAB_X = LINE1_ZAB_Mag * math.sin(LINE1_ZAB_Ang_radians)
            LINE1_Arr.extend([LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X])
            
            # Calculate LINE1_ZBC_Mag, Ang, R, X
            LINE1_ZBC_Mag = abs((LINE1_V2_Complex - LINE1_V3_Complex) / (LINE1_IL2_Complex - LINE1_IL3_Complex))
            LINE1_diff_V2_V3 = LINE1_V2_Complex - LINE1_V3_Complex
            LINE1_diff_IL2_IL3 = LINE1_IL2_Complex - LINE1_IL3_Complex
            LINE1_ZBC_Ang = math.degrees(math.atan2(LINE1_diff_V2_V3.imag, LINE1_diff_V2_V3.real) - math.atan2(LINE1_diff_IL2_IL3.imag, LINE1_diff_IL2_IL3.real))
            LINE1_ZBC_Ang_radians = math.radians(LINE1_ZBC_Ang)
            LINE1_ZBC_R = LINE1_ZBC_Mag * math.cos(LINE1_ZBC_Ang_radians)
            LINE1_ZBC_X = LINE1_ZBC_Mag * math.sin(LINE1_ZBC_Ang_radians)
            LINE1_Arr.extend([LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X])
            
            # Calculate LINE1_ZCA_Mag, Ang, R, X
            LINE1_ZCA_Mag = abs((LINE1_V3_Complex - LINE1_V1_Complex) / (LINE1_IL3_Complex - LINE1_IL1_Complex))
            LINE1_diff_V3_V1 = LINE1_V1_Complex - LINE1_V3_Complex #CEK LAGI KETIKA DIBALIK A-C hasil sama dengan excel, ketika C-A hasil berbeda dengan excel
            LINE1_diff_IL3_IL1 = LINE1_IL1_Complex - LINE1_IL3_Complex #CEK LAGI KETIKA DIBALIK A-C hasil sama dengan excel, ketika C-A hasil berbeda dengan excel
            LINE1_ZCA_Ang = math.degrees(math.atan2(LINE1_diff_V3_V1.imag, LINE1_diff_V3_V1.real) - math.atan2(LINE1_diff_IL3_IL1.imag, LINE1_diff_IL3_IL1.real))
            LINE1_ZCA_Ang_radians = math.radians(LINE1_ZCA_Ang)
            LINE1_ZCA_R = LINE1_ZCA_Mag * math.cos(LINE1_ZCA_Ang_radians)
            LINE1_ZCA_X = LINE1_ZCA_Mag * math.sin(LINE1_ZCA_Ang_radians)
            LINE1_Arr.extend([LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X])
            
            ###########################
            # Add code for LINE2 data reading and processing here
            ###########################
            
            
            # Monitor IN
            print(f"LINE1_IN_Complex : {LINE1_IN_Complex}")
            print(f"LINE1_IL1_Complex : {LINE1_IL1_Complex}")
            print(f"LINE1_V1_Complex : {LINE1_V1_Complex}")
            print(f"k0 : {LINE1_k0}")
            print(f"n0 : {LINE1_n0}")
            print(f"LINE1_ZA{LINE1_ZA}")
            print(f"LINE1_ZA_Real :{LINE1_ZA_Real}")
            print(f"LINE1_ZA_Imag :{LINE1_ZA_Imag}")

            print(f"LINE1_ZA_Mag : {LINE1_ZA_Mag}")
            print(f"LINE1_ZA_Ang : {LINE1_ZA_Ang}")
            print(f"LINE1_ZA_R : {LINE1_ZA_R}")
            print(f"LINE1_ZA_X : {LINE1_ZA_X}")	
            print(f"LINE1_ZB_Mag : {LINE1_ZB_Mag}")
            print(f"LINE1_ZB_Ang : {LINE1_ZB_Ang}")
            print(f"LINE1_ZB_R : {LINE1_ZB_R}")
            print(f"LINE1_ZB_X : {LINE1_ZB_X}")                
            print(f"LINE1_ZC_Mag : {LINE1_ZC_Mag}")
            print(f"LINE1_ZC_Ang : {LINE1_ZC_Ang}")
            print(f"LINE1_ZC_R : {LINE1_ZC_R}")
            print(f"LINE1_ZC_X : {LINE1_ZC_X}")
            print(f"LINE1_ZAB_Mag : {LINE1_ZAB_Mag}")	
            print(f"LINE1_ZAB_Ang : {LINE1_ZAB_Ang}")
            print(f"LINE1_ZAB_R : {LINE1_ZAB_R}")	
            print(f"LINE1_ZAB_X : {LINE1_ZAB_X}")
            print(f"LINE1_ZBC_Mag : {LINE1_ZBC_Mag}")	
            print(f"LINE1_ZBC_Ang : {LINE1_ZBC_Ang}")
            print(f"LINE1_ZBC_R : {LINE1_ZBC_R}")	
            print(f"LINE1_ZBC_X : {LINE1_ZBC_X}")
            print(f"LINE1_ZCA_Mag : {LINE1_ZCA_Mag}")	
            print(f"LINE1_ZCA_Ang : {LINE1_ZCA_Ang}")
            print(f"LINE1_ZCA_R : {LINE1_ZCA_R}")	
            print(f"LINE1_ZCA_X : {LINE1_ZCA_X}")

            data_to_write = {
                    'DATE' : datetime.now().strftime("%Y%M%D"), 'TIME' : datetime.now().strftime("%H:%M:%S"),
                    'LINE_IL1' : LINE1_IL1, 'LINE_IL1-Ang' : LINE1_Ang_I1, 
                    'LINE_IL2' : LINE1_IL2, 'LINE_IL2-Ang' : LINE1_Ang_I2,
                    'LINE_IL3' : LINE1_IL3, 'LINE_IL3-Ang' : LINE1_Ang_I3,
                    'LINE_UL1' : LINE1_U1, 'LINE_UL1-Ang' : LINE1_Ang_U1,
                    'LINE_UL2' : LINE1_U2, 'LINE_UL2-Ang' : LINE1_Ang_U2,
                    'LINE_UL3' : LINE1_U3, 'LINE_UL3-Ang' : LINE1_Ang_U3,
                    'LINE1_z0z1_mag' : LINE1_z0z1_mag, 'LINE1_z0z1_ang':LINE1_z0z1_ang,
                    'LINE1_IL1_Real' : LINE1_IL1_Real, 'LINE1_IL2_Real' : LINE1_IL2_Real, 'LINE1_IL3_Real' : LINE1_IL3_Real,
                    'LINE1_IL1_Imag' : LINE1_IL1_Imag, 'LINE1_IL2_Imag' : LINE1_IL2_Imag, 'LINE1_IL3_Imag' : LINE1_IL3_Imag,
                    'LINE1_V1_Real' : LINE1_V1_Real, 'LINE1_V2_Real' : LINE1_V2_Real, 'LINE1_V3_Real' : LINE1_V3_Real,
                    'LINE1_V1_Imag' : LINE1_V1_Imag, 'LINE1_V2_Imag' : LINE1_V2_Imag, 'LINE1_V3_Imag' : LINE1_V3_Imag,
                    'LINE1_IL1_Complex' : LINE1_IL1_Complex, 'LINE1_IL2_Complex' : LINE1_IL2_Complex, 'LINE1_IL3_Complex' : LINE1_IL3_Complex,
                    'LINE1_V1_Complex' : LINE1_V1_Complex, 'LINE1_V2_Complex' : LINE1_V2_Complex, 'LINE1_V3_Complex' : LINE1_V3_Complex,
                    'LINE1_IN_Imag' : LINE1_IN_Imag, 'LINE1_IN_Real' : LINE1_IN_Real, 'LINE1_IN_Mag' : LINE1_IN_Mag, 'LINE1_IN_Ang' : LINE1_IN_Ang 
                }

            await generate_csv(data_to_write)
            await asyncio.sleep(0.2)

            elapsed_time = datetime.now() - start_time
            if elapsed_time.total_seconds() >= 60:
                # Write data to CSV
                await generate_csv(data_to_write)
                print("Data written to CSV.")
                # Reset data and start time
                data_to_write = {}
                start_time = datetime.now()

            
            

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = [main_async()]
    loop.run_until_complete(asyncio.gather(*tasks))