# # import os
# # import influxdb_client
# # from influxdb_client.client.write_api import SYNCHRONOUS


# # bucket = "MyBucket"
# # token = "iuJUupeEeIyRK-m0_-OubrUYQSaLntH-nygu76O25d0fKQgLjHZGpQ1v77rBQ9xMR0zfeXkJ6xSmzDUn7l8gUw=="
# # org = "MyTeam"
# # url = "https://us-east-1-1.aws.cloud2.influxdata.com"

# # client = influxdb_client.InfluxDBClient(
# #     url=url,
# #     token=token,
# #     org=org
# # )


# # write_api = client.write_api(write_options=SYNCHRONOUS)
# # data = influxdb_client.Point("Information").tag("Voltage", 14).field("Current", 14)
# # write_api.write(bucket=bucket, org=org, record=data)

import os
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import random
import time

bucket = "sensor"
token = "d-lZs_deGKXlGAIzKR2bB1Zaiuy-c_j_J79yh4dvYJv4CbKtVErHt0Xt7ZPq7KStrCJyFRsvGzMA8TbFKjhRPg=="
org = "MyTeam"
url = "https://us-east-1-1.aws.cloud2.influxdata.com"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

try:
    while True:
        # Menghasilkan nilai acak untuk "Voltage" dan "Current"
        random_voltage = random.randint(1, 100)
        random_current = random.randint(1, 100)

        # Membuat poin dan menambahkan tag dan field
        data_point = influxdb_client.Point("Information").tag("Voltage", random_voltage).field("Current", random_current)

        # Menyimpan data ke InfluxDB
        write_api.write(bucket=bucket, org=org, record=data_point)

        # Cetak nilai yang disimpan
        print(f"Voltage: {random_voltage}, Current: {random_current}")

        # Menunggu 0.2 detik sebelum menyimpan data berikutnya
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Proses dihentikan.")
finally:
    client.close()
