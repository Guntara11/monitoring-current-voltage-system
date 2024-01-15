import random
import csv
from ftplib import FTP
import time
import os

ftp_host = 'ftpupload.net'
ftp_port = 21
ftp_user = 'if0_35759562'
ftp_password = '2c9y0xvm'
remote_file_path = './'
local_file_path = 'data.csv'

all_numbers = set(range(1, 101))
previous_data = []

while all_numbers:
    number = random.choice(list(all_numbers))
    print(number)

    all_numbers.remove(number)
    previous_data.append([number])

    # Trim previous_data to keep only the latest 5 rows
    previous_data = previous_data[-1:]

    # Write the new number to the CSV file
    with open('data.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(previous_data)

    # Upload the CSV file to the FTP server
    with FTP(ftp_host) as ftp:
        ftp.login(user=ftp_user, passwd=ftp_password)

        # Change to the desired remote directory
        ftp.cwd(remote_file_path)

        # Upload the file to the FTP server
        with open('data.csv', 'rb') as file:
            ftp.storbinary('STOR ' + local_file_path, file)

    # Wait for 2 seconds before the next iteration
    time.sleep(1)