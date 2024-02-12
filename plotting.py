            data_to_write = {
                    'Timestamp' : datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                    'DATE' : datetime.now().strftime("%Y-%m-%d"), 'TIME' : datetime.now().strftime("%H:%M:%S"),
                    'LINE_IL1' : LINE1_IL1, 'LINE_IL1-Ang' : LINE1_Ang_I1, 
                    'LINE_IL2' : LINE1_IL2, 'LINE_IL2-Ang' : LINE1_Ang_I2,
                    'LINE_IL3' : LINE1_IL3, 'LINE_IL3-Ang' : LINE1_Ang_I3,
                    'LINE_UL1' : LINE1_U1, 'LINE_UL1-Ang' : LINE1_Ang_U1,
                    'LINE_UL2' : LINE1_U2, 'LINE_UL2-Ang' : LINE1_Ang_U2,
                    'LINE_UL3' : LINE1_U3, 'LINE_UL3-Ang' : LINE1_Ang_U3,
                    'LINE1_z0z1_mag' : LINE1_z0z1_mag, 'LINE1_z0z1_ang':LINE1_z0z1_ang,
                    'LINE1_IL1_Real' : str(real_data[0]), 'LINE1_IL2_Real' : str(real_data[1]), 'LINE1_IL3_Real' : str(real_data[2]),
                    'LINE1_IL1_Imag' : str(imag_data[0]), 'LINE1_IL2_Imag' : str(imag_data[1]), 'LINE1_IL3_Imag' : str(imag_data[2]),
                    'LINE1_V1_Real' : str(real_data[3]), 'LINE1_V2_Real' : str(real_data[4]), 'LINE1_V3_Real' : str(real_data[5]),
                    'LINE1_V1_Imag' : str(imag_data[3]), 'LINE1_V2_Imag' : str(imag_data[4]), 'LINE1_V3_Imag' : str(imag_data[5]),
                    'LINE1_IL1_Complex' : str(complex_data[0]), 'LINE1_IL2_Complex' : str(complex_data[1]), 'LINE1_IL3_Complex' : str(complex_data[2]),
                    'LINE1_V1_Complex' : str(complex_data[3]), 'LINE1_V2_Complex' : str(complex_data[4]), 'LINE1_V3_Complex' : str(complex_data[5]),
                    'LINE1_IN_Imag' : str(LINE1_IN_Imag), 'LINE1_IN_Real' : str(LINE1_IN_Real), 'LINE1_IN_Mag' : str(LINE1_IN_Mag), 'LINE1_IN_Ang' : str(LINE1_IN_Ang) 
                }

            # Store Data to MongoDB
            collection.insert_one(data_to_write)
            time.sleep(0.2)
            # Generate File CSV 
            generate_csv(data_to_write)

            elapsed_time = datetime.now() - start_time
            if elapsed_time.total_seconds() >= 600:
                # Write data to CSV
                generate_csv(data_to_write)
                print("Data written to CSV.")
                # Reset data and start time
                data_to_write = {}
                start_time = datetime.now()