from ftplib import FTP
import time

ftp_host = 'ftpupload.net'
ftp_port = 21
ftp_user = 'if0_35759562'
ftp_password = '2c9y0xvm'
remote_file_path = 'data.csv'
local_file_path = 'downloaded_data.csv'

while True:
    # Download the file from the FTP server
    with FTP(ftp_host) as ftp:
        ftp.login(user=ftp_user, passwd=ftp_password)

        # Change to the desired remote directory
        ftp.cwd('/')

        # Download the file from the FTP server
        with open(local_file_path, 'wb') as file:
            ftp.retrbinary('RETR ' + remote_file_path, file.write)

    print(f"File downloaded from FTP: {local_file_path}")

    # Wait for 1 second before the next iteration
    time.sleep(1)
