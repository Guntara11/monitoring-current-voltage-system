import random
import csv
from ftplib import FTP
import time
import os

# FTP server credentials
ftp_host = 'ftpupload.net'
ftp_port = 21
ftp_user = 'if0_35759562'
ftp_password = '2c9y0xvm'
remote_file_path = './'
local_file_path = 'data.csv'

while True:
    # Generate a single random number
    number = random.randint(1, 100)

    # Read existing data from the CSV file if it exists
    existing_data = []
    if os.path.exists('data.csv'):
        with open('data.csv', 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            existing_data = list(csv_reader)

    # Append the new random number to the existing data
    existing_data.append([number])

    # Write the updated data to the CSV file
    with open('data.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(existing_data)

    # Upload the CSV file to the FTP server
    with FTP(ftp_host) as ftp:
        ftp.login(user=ftp_user, passwd=ftp_password)

        # Change to the desired remote directory
        ftp.cwd(remote_file_path)

        # Upload the file to the FTP server
        with open('data.csv', 'rb') as file:
            ftp.storbinary('STOR ' + local_file_path, file)

    # Wait for 2 seconds before the next iteration
    print(number)
    time.sleep(2)
