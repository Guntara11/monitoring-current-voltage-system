import asyncio
import time
import math
import cmath
import struct
from pymodbus.client import ModbusSerialClient
from aiogram import Bot, Dispatcher

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

async def main_async():
    # Set up Modbus serial connection for LINE1
    #client1 = ModbusSerialClient(method='rtu', port='COM9', baudrate=19200, stopbits=1, bytesize=8, parity='N')
    
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

            LINE1_U1 = 89236.961
            LINE1_U2 = 89521.813
            LINE1_U3 = 89844.727
            LINE1_Ang_U1 = 117.274
            LINE1_Ang_U2 = 356.92
            LINE1_Ang_U3 = 237.173

            LINE1_IL1 = 86.126
            LINE1_IL2 = 87.365
            LINE1_IL3 = 100.566
            LINE1_Ang_I1 = 112.977
            LINE1_Ang_I2 = 0.044
            LINE1_Ang_I3 = 232.82

            LINE1_z0z1_mag = 6.181
            LINE1_z0z1_ang = -2.55
            
            LINE1_xpz1 = 12.6875
            LINE1_xpz2 = 19
            LINE1_xpz3 = 25.375

            LINE1_rpz1 = 17.3125
            LINE1_rpz2 = 26
            LINE1_rpz3 = 34.625

            LINE1_xgz1 = 12.6875
            LINE1_xgz2 = 19
            LINE1_xgz3 = 25.375

            LINE1_rgz1 = 46.1875
            LINE1_rgz2 = 46.1875
            LINE1_rgz3 = 46.1875

            LINE1_angle= 75
            
            LINE1_z0z1_mag = 6.181
            LINE1_z0z1_ang = -2.55

            # Phase to Ground
            LINE1_Z1_PG_Real= LINE1_xgz1 * math.cos(math.radians(LINE1_angle))
            LINE1_Z2_PG_Real= LINE1_xgz2 * math.cos(math.radians(LINE1_angle))
            LINE1_Z3_PG_Real= LINE1_xgz3 * math.cos(math.radians(LINE1_angle))

            LINE1_Z1_PG_Imag= LINE1_xgz1 * math.sin(math.radians(LINE1_angle))
            LINE1_Z2_PG_Imag= LINE1_xgz2 * math.sin(math.radians(LINE1_angle))
            LINE1_Z3_PG_Imag= LINE1_xgz3 * math.sin(math.radians(LINE1_angle))

            LINE1_reach_z1_x= LINE1_Z1_PG_Real
            LINE1_reach_z1_y= LINE1_Z1_PG_Imag
            LINE1_reach_z2_x= LINE1_Z2_PG_Real
            LINE1_reach_z2_y= LINE1_Z2_PG_Imag
            LINE1_reach_z3_x= LINE1_Z3_PG_Real
            LINE1_reach_z3_y= LINE1_Z3_PG_Imag

            top_right_z1_x= LINE1_reach_z1_x + LINE1_rgz1
            top_right_z1_y= LINE1_reach_z1_y
            top_right_z2_x= LINE1_reach_z2_x + LINE1_rgz2
            top_right_z2_y= LINE1_reach_z2_y
            top_right_z3_x= LINE1_reach_z3_x + LINE1_rgz3
            top_right_z3_y= LINE1_reach_z3_y

            top_left_z1_x= LINE1_Z1_PG_Real-(0.5*LINE1_rgz1)
            top_left_z1_y= LINE1_reach_z1_y
            top_left_z2_x= LINE1_Z2_PG_Real-(0.5*LINE1_rgz2)
            top_left_z2_y= LINE1_reach_z2_y
            top_left_z3_x= LINE1_Z3_PG_Real-(0.5*LINE1_rgz3)
            top_left_z3_y= LINE1_reach_z3_y

            down_right_z1_x= LINE1_rgz1 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_right_z1_y= -LINE1_rgz1 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))
            down_right_z2_x= LINE1_rgz2 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_right_z2_y= -LINE1_rgz2 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))
            down_right_z3_x= LINE1_rgz3 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_right_z3_y= -LINE1_rgz3 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))

            down_left_z1_x= -0.5 * LINE1_rgz1 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_left_z1_y= 0.5 * LINE1_rgz1 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))
            down_left_z2_x= -0.5 * LINE1_rgz2 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_left_z2_y= 0.5 * LINE1_rgz2 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))
            down_left_z3_x= -0.5 * LINE1_rgz3 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_left_z3_y= 0.5 * LINE1_rgz3 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))

            right_side_z1_x= top_right_z1_x
            right_side_z1_y= LINE1_reach_z1_y
            right_side_z2_x= top_right_z2_x
            right_side_z2_y= LINE1_reach_z2_y
            right_side_z3_x= top_right_z3_x
            right_side_z3_y= LINE1_reach_z3_y

            left_side_z1_x= down_left_z1_x
            left_side_z1_y= down_left_z1_y
            left_side_z2_x= down_left_z2_x
            left_side_z2_y= down_left_z1_y
            left_side_z3_x= down_left_z3_x
            left_side_z3_y= down_left_z1_y

            # Cetak data dengan keterangan
            print("Phase_to_gnd")
            print("LINE1_Z1_PG_Real =", LINE1_Z1_PG_Real)
            print("LINE1_Z2_PG_Real =", LINE1_Z2_PG_Real)
            print("LINE1_Z3_PG_Real =", LINE1_Z3_PG_Real)
            print("LINE1_Z1_PG_Imag =", LINE1_Z1_PG_Imag)
            print("LINE1_Z2_PG_Imag =", LINE1_Z2_PG_Imag)
            print("LINE1_Z3_PG_Imag =", LINE1_Z3_PG_Imag)
            print("LINE1_reach_z1_x =", LINE1_reach_z1_x)
            print("LINE1_reach_z1_y =", LINE1_reach_z1_y)
            print("LINE1_reach_z2_x =", LINE1_reach_z2_x)
            print("LINE1_reach_z2_y =", LINE1_reach_z2_y)
            print("LINE1_reach_z3_x =", LINE1_reach_z3_x)
            print("LINE1_reach_z3_y =", LINE1_reach_z3_y)
            print("top_right_z1_x =", top_right_z1_x)
            print("top_right_z1_y =", top_right_z1_y)
            print("top_right_z2_x =", top_right_z2_x)
            print("top_right_z2_y =", top_right_z2_y)
            print("top_right_z3_x =", top_right_z3_x)
            print("top_right_z3_y =", top_right_z3_y)
            print("top_left_z1_x =", top_left_z1_x)
            print("top_left_z1_y =", top_left_z1_y)
            print("top_left_z2_x =", top_left_z2_x)
            print("top_left_z2_y =", top_left_z2_y)
            print("top_left_z3_x =", top_left_z3_x)
            print("top_left_z3_y =", top_left_z3_y)
            print("down_right_z1_x =", down_right_z1_x)
            print("down_right_z1_y =", down_right_z1_y)
            print("down_right_z2_x =", down_right_z2_x)
            print("down_right_z2_y =", down_right_z2_y)
            print("down_right_z3_x =", down_right_z3_x)
            print("down_right_z3_y =", down_right_z3_y)
            print("down_left_z1_x =", down_left_z1_x)
            print("down_left_z1_y =", down_left_z1_y)
            print("down_left_z2_x =", down_left_z2_x)
            print("down_left_z2_y =", down_left_z2_y)
            print("down_left_z3_x =", down_left_z3_x)
            print("down_left_z3_y =", down_left_z3_y)
            print("right_side_z1_x =", right_side_z1_x)
            print("right_side_z1_y =", right_side_z1_y)
            print("right_side_z2_x =", right_side_z2_x)
            print("right_side_z2_y =", right_side_z2_y)
            print("right_side_z3_x =", right_side_z3_x)
            print("right_side_z3_y =", right_side_z3_y)
            print("left_side_z1_x =", left_side_z1_x)
            print("left_side_z1_y =", left_side_z1_y)
            print("left_side_z2_x =", left_side_z2_x)
            print("left_side_z2_y =", left_side_z2_y)
            print("left_side_z3_x =", left_side_z3_x)
            print("left_side_z3_y =", left_side_z3_y)


            # Phase to Phase
            LINE1_Z1_PP_Real= LINE1_rpz1 * math.cos(math.radians(LINE1_angle))
            LINE1_Z2_PP_Real= LINE1_rpz2 * math.cos(math.radians(LINE1_angle))
            LINE1_Z3_PP_Real= LINE1_rpz3 * math.cos(math.radians(LINE1_angle))

            LINE1_Z1_PP_Imag= LINE1_rpz1 * math.sin(math.radians(LINE1_angle))
            LINE1_Z2_PP_Imag= LINE1_rpz2 * math.sin(math.radians(LINE1_angle))
            LINE1_Z3_PP_Imag= LINE1_rpz3 * math.sin(math.radians(LINE1_angle))

            LINE1_reach_z1_x= LINE1_Z1_PP_Real
            LINE1_reach_z1_y= LINE1_Z1_PP_Imag
            LINE1_reach_z2_x= LINE1_Z2_PP_Real
            LINE1_reach_z2_y= LINE1_Z2_PP_Imag
            LINE1_reach_z3_x= LINE1_Z3_PP_Real
            LINE1_reach_z3_y= LINE1_Z3_PP_Imag

            top_right_z1_x= LINE1_reach_z1_x + LINE1_rpz1
            top_right_z1_y= LINE1_reach_z1_y
            top_right_z2_x= LINE1_reach_z2_x + LINE1_rpz2
            top_right_z2_y= LINE1_reach_z2_y
            top_right_z3_x= LINE1_reach_z3_x + LINE1_rpz3
            top_right_z3_y= LINE1_reach_z3_y

            top_left_z1_x= LINE1_Z1_PP_Real-(0.5*LINE1_rpz1)
            top_left_z1_y= LINE1_reach_z1_y
            top_left_z2_x= LINE1_Z2_PP_Real-(0.5*LINE1_rpz2)
            top_left_z2_y= LINE1_reach_z2_y
            top_left_z3_x= LINE1_Z3_PP_Real-(0.5*LINE1_rpz3)
            top_left_z3_y= LINE1_reach_z3_y

            down_right_z1_x= LINE1_rpz1 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_right_z1_y= -LINE1_rpz1 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))
            down_right_z2_x= LINE1_rpz2 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_right_z1_y= -LINE1_rpz2 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))
            down_right_z3_x= LINE1_rpz3 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_right_z3_y= -LINE1_rpz3 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))

            down_left_z1_x= -0.5 * LINE1_rpz1 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_left_z1_y= 0.5 * LINE1_rpz1 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))
            down_left_z2_x= -0.5 * LINE1_rpz2 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_left_z2_y= 0.5 * LINE1_rpz2 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))
            down_left_z3_x= -0.5 * LINE1_rpz3 * math.sin(math.radians(LINE1_angle)) * math.cos(math.radians(90 - LINE1_angle))
            down_left_z3_y= 0.5 * LINE1_rpz3 * math.sin(math.radians(LINE1_angle)) * math.sin(math.radians(90 - LINE1_angle))

            right_side_z1_x= top_right_z1_x
            right_side_z1_y= LINE1_reach_z1_y
            right_side_z2_x= top_right_z2_x
            right_side_z2_y= LINE1_reach_z2_y
            right_side_z3_x= top_right_z3_x
            right_side_z3_y= LINE1_reach_z3_y

            left_side_z1_x= down_left_z1_x
            left_side_z1_y= down_left_z1_y
            left_side_z2_x= down_left_z2_x
            left_side_z2_y= down_left_z1_y
            left_side_z3_x= down_left_z3_x
            left_side_z3_y= down_left_z1_y

            print("Phase_to_phase")
            print("LINE1_Z1_PP_Real =", LINE1_Z1_PP_Real)
            print("LINE1_Z2_PP_Real =", LINE1_Z2_PP_Real)
            print("LINE1_Z3_PP_Real =", LINE1_Z3_PP_Real)
            print("LINE1_Z1_PP_Imag =", LINE1_Z1_PP_Imag)
            print("LINE1_Z2_PP_Imag =", LINE1_Z2_PP_Imag)
            print("LINE1_Z3_PP_Imag =", LINE1_Z3_PP_Imag)
            print("LINE1_reach_z1_x =", LINE1_reach_z1_x)
            print("LINE1_reach_z1_y =", LINE1_reach_z1_y)
            print("LINE1_reach_z2_x =", LINE1_reach_z2_x)
            print("LINE1_reach_z2_y =", LINE1_reach_z2_y)
            print("LINE1_reach_z3_x =", LINE1_reach_z3_x)
            print("LINE1_reach_z3_y =", LINE1_reach_z3_y)
            print("top_right_z1_x =", top_right_z1_x)
            print("top_right_z1_y =", top_right_z1_y)
            print("top_right_z2_x =", top_right_z2_x)
            print("top_right_z2_y =", top_right_z2_y)
            print("top_right_z3_x =", top_right_z3_x)
            print("top_right_z3_y =", top_right_z3_y)
            print("top_left_z1_x =", top_left_z1_x)
            print("top_left_z1_y =", top_left_z1_y)
            print("top_left_z2_x =", top_left_z2_x)
            print("top_left_z2_y =", top_left_z2_y)
            print("top_left_z3_x =", top_left_z3_x)
            print("top_left_z3_y =", top_left_z3_y)
            print("down_right_z1_x =", down_right_z1_x)
            print("down_right_z1_y =", down_right_z1_y)
            print("down_right_z2_x =", down_right_z2_x)
            print("down_right_z2_y =", down_right_z2_y)
            print("down_right_z3_x =", down_right_z3_x)
            print("down_right_z3_y =", down_right_z3_y)
            print("down_left_z1_x =", down_left_z1_x)
            print("down_left_z1_y =", down_left_z1_y)
            print("down_left_z2_x =", down_left_z2_x)
            print("down_left_z2_y =", down_left_z2_y)
            print("down_left_z3_x =", down_left_z3_x)
            print("down_left_z3_y =", down_left_z3_y)
            print("right_side_z1_x =", right_side_z1_x)
            print("right_side_z1_y =", right_side_z1_y)
            print("right_side_z2_x =", right_side_z2_x)
            print("right_side_z2_y =", right_side_z2_y)
            print("right_side_z3_x =", right_side_z3_x)
            print("right_side_z3_y =", right_side_z3_y)
            print("left_side_z1_x =", left_side_z1_x)
            print("left_side_z1_y =", left_side_z1_y)
            print("left_side_z2_x =", left_side_z2_x)
            print("left_side_z2_y =", left_side_z2_y)
            print("left_side_z3_x =", left_side_z3_x)
            print("left_side_z3_y =", left_side_z3_y)

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
            LINE1_IN_Mag = math.sqrt(LINE1_IN_Real*2 + LINE1_IN_Imag*2)

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
            LINE1_ZA_Complex = LINE1_V1_Complex / sum_result

            LINE1_ZA_Real = LINE1_ZA_Complex.real
            LINE1_ZA_Imag = LINE1_ZA_Complex.imag
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
            LINE1_ZB_Complex = LINE1_V2_Complex / sum_result

            LINE1_ZB_Real = LINE1_ZB_Complex.real
            LINE1_ZB_Imag = LINE1_ZB_Complex.imag
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
            LINE1_ZC_Complex = LINE1_V3_Complex / sum_result

            LINE1_ZC_Real = LINE1_ZC_Complex.real
            LINE1_ZC_Imag = LINE1_ZC_Complex.imag
            LINE1_Arr.extend([LINE1_ZC_Real, LINE1_ZC_Imag])


            LINE1_ZC_Mag = abs(LINE1_V3_Complex / LINE1_IL3_Complex)
            LINE1_ZC_Ang = math.degrees(cmath.phase(LINE1_V3_Complex / LINE1_IL3_Complex))					
            LINE1_ZC_Ang_radians = math.radians(LINE1_ZC_Ang)
            LINE1_ZC_R = LINE1_ZC_Mag * math.cos(LINE1_ZC_Ang_radians)
            LINE1_ZC_X = LINE1_ZC_Mag * math.sin(LINE1_ZC_Ang_radians)
            LINE1_Arr.extend([LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X])

                                
            # Calculate LINE1_ZAB_Mag, Ang, R, X
            LINE1_ZAB_Complex = (LINE1_V1_Complex - LINE1_V2_Complex) / (LINE1_IL1_Complex - LINE1_IL2_Complex)
            LINE1_ZAB_Real = LINE1_ZAB_Complex.real
            LINE1_ZAB_Imag = LINE1_ZAB_Complex.imag

            
            LINE1_ZAB_Mag = abs((LINE1_V1_Complex - LINE1_V2_Complex) / (LINE1_IL1_Complex - LINE1_IL2_Complex))
            LINE1_diff_V1_V2 = LINE1_V1_Complex - LINE1_V2_Complex
            LINE1_diff_IL1_IL2 = LINE1_IL1_Complex - LINE1_IL2_Complex
            LINE1_ZAB_Ang = math.degrees(math.atan2(LINE1_diff_V1_V2.imag, LINE1_diff_V1_V2.real) - math.atan2(LINE1_diff_IL1_IL2.imag, LINE1_diff_IL1_IL2.real))
            LINE1_ZAB_Ang_radians = math.radians(LINE1_ZAB_Ang)
            LINE1_ZAB_R = LINE1_ZAB_Mag * math.cos(LINE1_ZAB_Ang_radians)
            LINE1_ZAB_X = LINE1_ZAB_Mag * math.sin(LINE1_ZAB_Ang_radians)
            LINE1_Arr.extend([LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X])
            
            # Calculate LINE1_ZBC_Mag, Ang, R, X
            LINE1_ZBC_Complex = (LINE1_V2_Complex - LINE1_V3_Complex) / (LINE1_IL2_Complex - LINE1_IL3_Complex)
            LINE1_ZBC_Real = LINE1_ZBC_Complex.real
            LINE1_ZBC_Imag = LINE1_ZBC_Complex.imag

            LINE1_ZBC_Mag = abs((LINE1_V2_Complex - LINE1_V3_Complex) / (LINE1_IL2_Complex - LINE1_IL3_Complex))
            LINE1_diff_V2_V3 = LINE1_V2_Complex - LINE1_V3_Complex
            LINE1_diff_IL2_IL3 = LINE1_IL2_Complex - LINE1_IL3_Complex
            LINE1_ZBC_Ang = math.degrees(math.atan2(LINE1_diff_V2_V3.imag, LINE1_diff_V2_V3.real) - math.atan2(LINE1_diff_IL2_IL3.imag, LINE1_diff_IL2_IL3.real))
            LINE1_ZBC_Ang_radians = math.radians(LINE1_ZBC_Ang)
            LINE1_ZBC_R = LINE1_ZBC_Mag * math.cos(LINE1_ZBC_Ang_radians)
            LINE1_ZBC_X = LINE1_ZBC_Mag * math.sin(LINE1_ZBC_Ang_radians)
            LINE1_Arr.extend([LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X])
            
            # Calculate LINE1_ZCA_Mag, Ang, R, X
            LINE1_ZCA_Complex = (LINE1_V3_Complex - LINE1_V1_Complex) / (LINE1_IL3_Complex - LINE1_IL1_Complex)
            LINE1_ZCA_Real = LINE1_ZCA_Complex.real
            LINE1_ZCA_Imag = LINE1_ZCA_Complex.imag

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
            
            print("____________")
            # Monitor IN
            print(f"k0 : {LINE1_k0}")
            print(f"n0 : {LINE1_n0}")
            print(f"LINE1_ZA_Real :{LINE1_ZA_Real}")
            print(f"LINE1_ZA_Imag :{LINE1_ZA_Imag}")            
            print(f"LINE1_ZB_Real :{LINE1_ZB_Real}")
            print(f"LINE1_ZB_Imag :{LINE1_ZB_Imag}")
            print(f"LINE1_ZC_Real :{LINE1_ZC_Real}")
            print(f"LINE1_ZC_Imag :{LINE1_ZC_Imag}")

            print(f"LINE1_ZAB_Real :{LINE1_ZAB_Real}")
            print(f"LINE1_ZAB_Imag :{LINE1_ZAB_Imag}")  
            
            print(f"LINE1_ZBC_Real :{LINE1_ZBC_Real}")
            print(f"LINE1_ZBC_Imag :{LINE1_ZBC_Imag}")  
            
            print(f"LINE1_ZCA_Real :{LINE1_ZCA_Real}")
            print(f"LINE1_ZCA_Imag :{LINE1_ZCA_Imag}")  


            await asyncio.sleep(1)  # Wait for 1 second before the next read

   
            

if __name__ == "_main_":
    loop = asyncio.get_event_loop()
    tasks = [main_async()]
    loop.run_until_complete(asyncio.gather(*tasks))