import random
import time
from utils import LineCalculation


# # Function to get real data
# def get_real_data(parsed_data):
#     return parsed_data[:6]

# # Function to get imaginary data
# def get_imag_data(parsed_data):
#     return parsed_data[6:12]

# # Function to get complex data
# def get_complex_data(parsed_data):
#     return parsed_data[12:]

# def get_line1_IN_data(parsed_data):
#     return parsed_data[:2]

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
                                LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                                LINE1_z0z1_mag, LINE1_z0z1_ang)

    # Get real and imag  data
    real_data = line_calc.get_real_data()
    imag_data = line_calc.get_imag_data()

    # Unpack real data
    IL1_Real, IL2_Real, IL3_Real, V1_Real, V2_Real, V3_Real = real_data
    # Unpack imaginary data
    IL1_Imag, IL2_Imag, IL3_Imag, V1_Imag, V2_Imag, V3_Imag = imag_data

    # Printing data
    print("Real Data:", real_data)
    print("IL1_Real = {0}\nIL2_Real = {1}\nIL3_Real = {2}".format(IL1_Real, IL2_Real, IL3_Real))
    print("V1_Real = {0}\nV2_Real = {1}\nV3_Real = {2}".format(V1_Real, V2_Real, V3_Real))

    print("Imaginary Data:", imag_data)
    print("IL1_Imag = {0}\nIL2_Imag = {1}\nIL3_Imag = {2}".format(IL1_Imag, IL2_Imag, IL3_Imag))
    print("V1_Imag = {0}\nV2_Imag = {1}\nV3_Imag = {2}".format(V1_Imag, V2_Imag, V3_Imag))


    complex_data = line_calc.get_complex_data()

    # Unpack complex data
    IL1_Complex, IL2_Complex, IL3_Complex, V1_Complex, V2_Complex, V3_Complex = complex_data

    print("Complex Data:", complex_data)
    print("IL1_Complex = {0}\nIL2_Complex = {1}\nIL3_Complex = {2}".format(IL1_Complex, IL2_Complex, IL3_Complex))
    print("V1_Complex = {0}\nV2_Complex = {1}\nV3_Complex = {2}".format(V1_Complex, V2_Complex, V3_Complex))


    line1_IN_data = line_calc.get_line1_IN_data()

    #Unpack LINE1_IN_data 
    LINE1_IN_Real, LINE1_IN_Imag, LINE1_IN_Complex, LINE1_IN_Mag, LINE1_IN_Ang = line1_IN_data
    print("LINE_IN data :", line1_IN_data)
    print("LINE1_IN_Complex = {0}\nLINE1_IN_Imag = {1}\nLiNE1_IN_Real = {2}\nLINE1_IN_Mag{3}\nLiNE1_IN_Ang".format(LINE1_IN_Complex, LINE1_IN_Imag, LINE1_IN_Real, LINE1_IN_Mag, LINE1_IN_Ang))

    k0 = line_calc.get_LINE1_k0()
    n0 = line_calc.get_LINE1_n0()
    product_result = line_calc.get_LINE1_PR()
    print("k0 = {0}\nn0 = {1}\nproduct result = {2}".format(k0, n0, product_result))

    
    za_data = line_calc.get_ZA_data()
    #unpack data
    LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = za_data
    #print data 
    print("LINE1_ZA_data", za_data)
    print("LINE1_ZA_Real = {0}\nLINE1_ZA_Imag = {1}\nLINE1_ZA_Mag = {2}\nLINE1_ZA_Ang = {3}\nLINE1_ZA_R = {4}\nLINE1_ZA_X = {5}"
          .format(LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X))
    
    zb_data = line_calc.get_ZB_data()
    #unpack data
    LINE1_ZB_Real, LINE1_ZB_Imag, LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X = zb_data
    print("LINE1_ZB_data", zb_data)
    print("LINE1_ZB_Real = {0}\nLINE1_ZB_Imag = {1}\nLINE1_ZB_Mag = {2}\nLINE1_ZB_Ang = {3}\nLINE1_ZB_R = {4}\nLINE1_ZB_X = {5}"
          .format(LINE1_ZB_Real, LINE1_ZB_Imag, LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X))
    
    zc_data = line_calc.get_ZC_data()
    #unpack data
    LINE1_ZC_Real, LINE1_ZC_Imag, LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X = zc_data
    print("LINE1_ZC_data", zc_data)
    print("LINE1_ZC_Real = {0}\nLINE1_ZC_Imag = {1}\nLINE1_ZC_Mag = {2}\nLINE1_ZC_Ang = {3}\nLINE1_ZC_R = {4}\nLINE1_ZC_X = {5}"
        .format(LINE1_ZC_Real, LINE1_ZC_Imag, LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X))
    
    zab_data = line_calc.get_ZAB_data()
    #unpack data
    LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X = zab_data
    #print data 
    print("LINE1_ZAB_data", zab_data)
    print("LINE1_ZAB_Mag = {0}\nLINE1_ZAB_Ang = {1}\nLINE1_ZAB_R = {2}\nLINE1_ZAB_X = {3}".format(LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X))

    zbc_data = line_calc.get_ZBC_data()
    #unpack data
    LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X = zbc_data
    #print data 
    print("LINE1_ZBC_data", zbc_data)
    print("LINE1_ZBC_Mag = {0}\nLINE1_ZBC_Ang = {1}\nLINE1_ZBC_R = {2}\nLINE1_ZBC_X = {3}".format(LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X))

    zca_data = line_calc.get_ZCA_data()
    #unpack data
    LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X = zca_data
    #print data 
    print("LINE1_ZCA_data", zca_data)
    print("LINE1_ZCA_Mag = {0}\nLINE1_ZCA_Ang = {1}\nLINE1_ZCA_R = {2}\nLINE1_ZCA_X = {3}".format(LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X))
    

    
    time.sleep(10)
