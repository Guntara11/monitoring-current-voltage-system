import numpy as np
import matplotlib.pyplot as plt
import random

plt.ion()  # interactive mode for real-time plots

x_values_voltage = []
y_values_voltage = []

x_values_current = []
y_values_current = []

fig, ax = plt.subplots()

while True:
    # input data random from 1 - 100
    data = {
        "voltage" : random.randint(1, 100),
        "current" : random.randint(1, 100),
    }
    
    # Assign to voltage or current randomly
    if random.choice([True, False]):  
        x_values_voltage.append(data['voltage'])
        y_values_voltage.append(data['current'])
        color = 'red'
    else:
        x_values_current.append(data['voltage'])
        y_values_current.append(data['current'])
        color = 'blue'

    # print voltage and current value
    print("Voltage: ", data['voltage'])
    print("Current: ", data['current'])

    # Plot voltage
    ax.scatter(x_values_voltage, y_values_voltage, color='red', label='Voltage')
    
    # Plot current
    ax.scatter(x_values_current, y_values_current, color='blue', label='Current')

    # Display x and y axis lines
    ax.axhline(0, color='black',linewidth=0.5)
    ax.axvline(0, color='black',linewidth=0.5)

    # Pause to allow time for the plot to be seen
    plt.pause(0.2)  