import numpy as np
import matplotlib.pyplot as plt
import random

plt.ion()  # interactive mode for real-time plots

x_values_voltage = []
y_values_current = []

fig, ax = plt.subplots()

while True:
    # input data random from 1 - 100
    data = {
        "voltage" : random.randint(1, 100),
        "current" : random.randint(1, 100),
    }
 
    x_values_voltage.append(data['voltage'])
    y_values_current.append(data['current'])

    # print voltage and current value
    print(f"Voltage : {data['voltage']}, Current : {data['current']}")

    # Plot data x dan y
    ax.scatter(data['voltage'], data['current'])

    # Pause to allow time for the plot to be seen
    plt.pause(0.2)  