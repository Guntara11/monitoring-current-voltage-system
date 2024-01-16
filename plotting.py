import numpy as np
import matplotlib.pyplot as plt

plt.ion()  # Mengaktifkan mode interaktif untuk plot real-time

x_values = []
y_values = []

fig, ax = plt.subplots()

i = 0
while True:
    number = np.random.randint(1, 101)
    x_values.append(i)
    print("data: ", number)
    y_values.append(number)
    i += 1
    ax.scatter(x_values, y_values)
    plt.pause(0.2)  # Pause untuk memberikan waktu agar plot dapat terlihat
    
plt.show()
