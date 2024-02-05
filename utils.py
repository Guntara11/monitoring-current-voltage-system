import math

class LineCalculation:
    def __init__(self):
        self.LINE1_IL_Real = []
        self.LINE1_IL_Imag = []
        self.LINE1_V_Real = []
        self.LINE1_V_Imag = []
        self.LINE1_IL_Complex = []
        self.LINE1_V_Complex = []
        self.LINE1_IN_Complex = None
        self.LINE1_Arr = []
        self.LINE1_V_Arr = []
        self.LINE1_I_Arr = []
        self.LINE1_IN_Arr = []

    def calculate_values(self, LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                         LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                         LINE1_z0z1_mag, LINE1_z0z1_ang):
        self.calculate_IL_Real(LINE1_IL1, LINE1_Ang_I1)
        self.calculate_IL_Imag(LINE1_IL1, LINE1_Ang_I1)
        self.calculate_IL_Complex()

        self.calculate_V_Real(LINE1_U1, LINE1_Ang_U1)
        self.calculate_V_Imag(LINE1_U1, LINE1_Ang_U1)
        self.calculate_V_Complex()

        self.calculate_IN_Complex()

        # Add more calculations as needed
        self.calculate_IN_Imag_Real_Mag_Ang()
        self.calculate_V_I_IN_Arr()

    def calculate_IL_Real(self, IL, angle):
        # Calculate IL_Real using the formula
        IL_Real = IL * math.cos(math.radians(angle))
        self.LINE1_IL_Real.append(IL_Real)

    def calculate_IL_Imag(self, IL, angle):
        # Calculate IL_Imag using the formula
        IL_Imag = IL * math.sin(math.radians(angle))
        self.LINE1_IL_Imag.append(IL_Imag)

    def calculate_IL_Complex(self):
        # Create complex numbers for LINE1_IL_Complex
        IL_Complex = complex(self.LINE1_IL_Real[-1], self.LINE1_IL_Imag[-1])
        self.LINE1_IL_Complex.append(IL_Complex)

    def calculate_V_Real(self, U, angle):
        # Calculate V_Real using the formula
        V_Real = U * math.cos(math.radians(angle))
        self.LINE1_V_Real.append(V_Real)

    def calculate_V_Imag(self, U, angle):
        # Calculate V_Imag using the formula
        V_Imag = U * math.sin(math.radians(angle))
        self.LINE1_V_Imag.append(V_Imag)

    def calculate_V_Complex(self):
        # Create complex numbers for LINE1_V_Complex
        V_Complex = complex(self.LINE1_V_Real[-1], self.LINE1_V_Imag[-1])
        self.LINE1_V_Complex.append(V_Complex)

    def calculate_IN_Complex(self):
        # Calculate LINE1_IN_Complex as the sum of LINE1_IL_Complex, LINE1_IL2_Complex, and LINE1_IL3_Complex
        self.LINE1_IN_Complex = sum(self.LINE1_IL_Complex)

    def calculate_IN_Imag_Real_Mag_Ang(self):
        # Calculate LINE1_IN_Imag and LINE1_IN_Real
        LINE1_IN_Imag = self.LINE1_IN_Complex.imag
        LINE1_IN_Real = self.LINE1_IN_Complex.real

        # Calculate LINE1_IN_Mag
        LINE1_IN_Mag = math.sqrt(LINE1_IN_Real**2 + LINE1_IN_Imag**2)

        # Calculate LINE1_IN_Ang
        LINE1_IN_Ang = math.degrees(math.atan2(LINE1_IN_Imag, LINE1_IN_Real))

        self.LINE1_Arr.extend([LINE1_IN_Mag, LINE1_IN_Ang, LINE1_IN_Real, LINE1_IN_Imag, self.LINE1_IN_Complex])

    def calculate_V_I_IN_Arr(self):
        # Add the calculated variables to the arrays
        self.LINE1_V_Arr = [self.LINE1_V_Real[-1], self.LINE1_V_Imag[-1]]
        self.LINE1_I_Arr = [self.LINE1_IL_Real[-1], self.LINE1_IL_Imag[-1]]
        self.LINE1_IN_Arr = [self.LINE1_IN_Complex.real, self.LINE1_IN_Complex.imag, self.LINE1_IN_Complex]

    def get_results(self):
        self.LINE1_Arr.extend(self.LINE1_IL_Real)
        self.LINE1_Arr.extend(self.LINE1_IL_Imag)
        self.LINE1_Arr.extend(self.LINE1_V_Real)
        self.LINE1_Arr.extend(self.LINE1_V_Imag)
        if self.LINE1_IN_Complex is not None:
            self.LINE1_Arr.extend([self.LINE1_IN_Complex.real, self.LINE1_IN_Complex.imag])
        return self.LINE1_Arr
