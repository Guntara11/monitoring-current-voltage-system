import random
import time

# Membuat set dari angka 1 sampai 100
all_numbers = set(range(1, 101))

while all_numbers:
    number = random.choice(list(all_numbers))
    print(number)

    all_numbers.remove(number)
    time.sleep(0.2)