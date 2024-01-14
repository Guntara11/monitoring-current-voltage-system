import random
import time

# Membuat set dari angka 1 sampai 100
all_numbers = set(range(1, 101))
data_count = 0
previous_data = []

while all_numbers:
    number = random.choice(list(all_numbers))
    print(number)

    all_numbers.remove(number)
    data_count += 1
    previous_data.append(number)

    time.sleep(0.2)

    if data_count == 50:
        # Print previous data
        print("data:", previous_data)
        
        # Update data
        print("Update data...")
        all_numbers = set(range(1, 101))
        data_count = 0
        previous_data = []