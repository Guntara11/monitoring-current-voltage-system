import random
import time
from utils import LineCalculation

while True:
    # Generate random values in main.py
    LINE1_U1 = random.uniform(80000, 90000)
    LINE1_U2 = random.uniform(80000, 90000)
    LINE1_U3 = random.uniform(80000, 90000)
    LINE1_Ang_U1 = random.uniform(0, 360)
    LINE1_Ang_U2 = random.uniform(0, 360)
    LINE1_Ang_U3 = random.uniform(0, 360)

    LINE1_IL1 = random.uniform(80, 120)
    LINE1_Ang_I1 = random.uniform(0, 360)
    LINE1_Ang_I2 = random.uniform(0, 360)

    LINE1_z0z1_mag = random.uniform(5, 7)
    LINE1_z0z1_ang = random.uniform(-5, 5)

    # Create LineCalculation object and pass random values
    line_calc = LineCalculation()
    line_calc.calculate_values(LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                                LINE1_IL1, LINE1_U2, LINE1_IL1, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I2,
                                LINE1_z0z1_mag, LINE1_z0z1_ang)

    results = line_calc.get_results()
    print(results)
    time.sleep(2)