import matplotlib.pyplot as plt
import random
import json

# membaca datd didalam config.json
with open('config.json', 'r') as json_file:
    impedance_point = json.load(json_file)

x_values_voltage = []
y_values_current = []

fig, ax = plt.subplots()

# Mengekstrak nilai x, y dari dictionary
x_values = [point["x"] for point in impedance_point.values()]
y_values = [point["y"] for point in impedance_point.values()]

# Memplot data dengan garis
plt.plot(x_values, y_values, marker='o', linestyle='-', color='red')

# Menambahkan garis sumbu x dan y
plt.axhline(0, color='black', linewidth=1)
plt.axvline(0, color='black', linewidth=1)

while True:
    data = {
        "voltage": random.randint(-20, 20),
        "current": random.randint(-20, 20),
    }

    x_values_voltage.append(data['voltage'])
    y_values_current.append(data['current'])
    # print voltage and current value
    print(f"Voltage: {data['voltage']}, Current: {data['current']}")
    # Plot data x dan y
    ax.scatter(data['voltage'], data['current'])
    # Pause to allow time for the plot to be seen
    plt.pause(0.2)