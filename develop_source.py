import random
import time
from utils import LineCalculation


# Function to get real data
def get_real_data(parsed_data):
    return parsed_data[:6]

# Function to get imaginary data
def get_imag_data(parsed_data):
    return parsed_data[6:12]

# Function to get complex data
def get_complex_data(parsed_data):
    return parsed_data[12:]

while True:
    # Generate random values
    # LINE1_U1 = random.uniform(80000, 90000)
    # LINE1_U2 = random.uniform(80000, 90000)
    # LINE1_U3 = random.uniform(80000, 90000)
    # LINE1_Ang_U1 = random.uniform(0, 360)
    # LINE1_Ang_U2 = random.uniform(0, 360)
    # LINE1_Ang_U3 = random.uniform(0, 360)

    # LINE1_IL1 = random.uniform(80, 120)
    # LINE1_IL2 = random.uniform(80, 120)
    # LINE1_IL3 = random.uniform(80, 120)
    # LINE1_Ang_I1 = random.uniform(0, 360)
    # LINE1_Ang_I2 = random.uniform(0, 360)
    # LINE1_Ang_I3 = random.uniform(0, 360)

    # LINE1_z0z1_mag = random.uniform(5, 7)
    # LINE1_z0z1_ang = random.uniform(-5, 5)

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
    # Create LineCalculation object and pass random values
    line_calc = LineCalculation()
    line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                LINE1_IL1, LINE1_U2, LINE1_IL1, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I2,
                                LINE1_z0z1_mag, LINE1_z0z1_ang)

    # Get parsed data
    real_data = line_calc.get_real_data()
    imag_data = line_calc.get_imag_data()
    complex_data = line_calc.get_complex_data()


    # Unpack real data
    IL1_Real, IL2_Real, IL3_Real, V1_Real, V2_Real, V3_Real = real_data

    # Unpack imaginary data
    IL1_Imag, IL2_Imag, IL3_Imag, V1_Imag, V2_Imag, V3_Imag = imag_data

    # Unpack complex data
    IL1_Complex, IL2_Complex, IL3_Complex, V1_Complex, V2_Complex, V3_Complex, LINE1_IN_Complex = complex_data

    # Printing data
    print("Real Data:", real_data)
    print("IL1_Real = {0}\nIL2_Real = {1}\nIL3_Real = {2}".format(IL1_Real, IL2_Real, IL3_Real))
    print("V1_Real = {0}\nV2_Real = {1}\nV3_Real = {2}".format(V1_Real, V2_Real, V3_Real))

    print("Imaginary Data:", imag_data)
    print("IL1_Imag = {0}\nIL2_Imag = {1}\nIL3_Imag = {2}".format(IL1_Imag, IL2_Imag, IL3_Imag))
    print("V1_Imag = {0}\nV2_Imag = {1}\nV3_Imag = {2}".format(V1_Imag, V2_Imag, V3_Imag))

    print("Complex Data:", complex_data)
    print("IL1_Complex = {0}\nIL2_Complex = {1}\nIL3_Complex = {2}".format(IL1_Complex, IL2_Complex, IL3_Complex))
    print("V1_Complex = {0}\nV2_Complex = {1}\nV3_Complex = {2}".format(V1_Complex, V2_Complex, V3_Complex))
    print("LINE1_IN_Complex =", LINE1_IN_Complex)

    time.sleep(2)
