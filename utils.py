import math

class LineCalculation:
    def __init__(self):
        self.real_data = []
        self.imag_data = []
        self.complex_data = []

    def calculate_values(self, LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                         LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                         LINE1_z0z1_mag, LINE1_z0z1_ang):
        self.calculate_IL_real_imag(LINE1_IL1, LINE1_Ang_I1, LINE1_IL2, LINE1_Ang_I2, LINE1_IL3, LINE1_Ang_I3)
        self.calculate_V_real_imag(LINE1_U1, LINE1_Ang_U1, LINE1_U2, LINE1_Ang_U2, LINE1_U3, LINE1_Ang_U3)
        self.create_complex_data()

    def calculate_IL_real_imag(self, IL1, Ang_I1, IL2, Ang_I2, IL3, Ang_I3):
        # Calculate real and imaginary parts of IL1, IL2, and IL3
        IL1_Real = IL1 * math.cos(math.radians(Ang_I1))
        IL1_Imag = IL1 * math.sin(math.radians(Ang_I1))
        IL2_Real = IL2 * math.cos(math.radians(Ang_I2))
        IL2_Imag = IL2 * math.sin(math.radians(Ang_I2))
        IL3_Real = IL3 * math.cos(math.radians(Ang_I3))
        IL3_Imag = IL3 * math.sin(math.radians(Ang_I3))

        self.real_data.extend([IL1_Real, IL2_Real, IL3_Real])
        self.imag_data.extend([IL1_Imag, IL2_Imag, IL3_Imag])

    def calculate_V_real_imag(self, U1, Ang_U1, U2, Ang_U2, U3, Ang_U3):
        # Calculate real and imaginary parts of V1, V2, and V3
        V1_Real = U1 * math.cos(math.radians(Ang_U1))
        V1_Imag = U1 * math.sin(math.radians(Ang_U1))
        V2_Real = U2 * math.cos(math.radians(Ang_U2))
        V2_Imag = U2 * math.sin(math.radians(Ang_U2))
        V3_Real = U3 * math.cos(math.radians(Ang_U3))
        V3_Imag = U3 * math.sin(math.radians(Ang_U3))

        self.real_data.extend([V1_Real, V2_Real, V3_Real])
        self.imag_data.extend([V1_Imag, V2_Imag, V3_Imag])

    def create_complex_data(self):
        # Create complex numbers for IL1, IL2, IL3, V1, V2, and V3
        IL1_complex = complex(self.real_data[0], self.imag_data[0])
        IL2_complex = complex(self.real_data[1], self.imag_data[1])
        IL3_complex = complex(self.real_data[2], self.imag_data[2])

        V1_complex = complex(self.real_data[3], self.imag_data[3])
        V2_complex = complex(self.real_data[4], self.imag_data[4])
        V3_complex = complex(self.real_data[5], self.imag_data[5])

        self.complex_data.extend([IL1_complex, IL2_complex, IL3_complex,
                                  V1_complex, V2_complex, V3_complex])

        LINE1_IN_Complex = IL1_complex + IL2_complex + IL3_complex
        self.complex_data.append(LINE1_IN_Complex)
    def get_real_data(self):
        return self.real_data

    def get_imag_data(self):
        return self.imag_data

    def get_complex_data(self):
        return self.complex_data
