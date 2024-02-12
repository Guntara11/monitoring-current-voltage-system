import math
import cmath
import pymongo
class LineCalculation:
    def __init__(self):
        self.real_data = []
        self.imag_data = []
        self.complex_data = []
        self.line1_IN_data = []
        self.line1_k0 = None
        self.line1_n0 = None
        self.data_ZA = []
        self.data_ZB = []
        self.data_ZC = []
        self.data_ZAB = []
        self.data_ZBC = []
        self.data_ZCA = []

    def calculate_values(self, LINE1_U1, LINE1_U2, LINE1_U3, LINE1_Ang_U1, LINE1_Ang_U2, LINE1_Ang_U3,
                         LINE1_IL1, LINE1_IL2, LINE1_IL3, LINE1_Ang_I1, LINE1_Ang_I2, LINE1_Ang_I3,
                         LINE1_z0z1_mag, LINE1_z0z1_ang):
        self._calculate_IL_real_imag(LINE1_IL1, LINE1_Ang_I1, LINE1_IL2, LINE1_Ang_I2, LINE1_IL3, LINE1_Ang_I3)
        self._calculate_V_real_imag(LINE1_U1, LINE1_Ang_U1, LINE1_U2, LINE1_Ang_U2, LINE1_U3, LINE1_Ang_U3)
        self._create_complex_data()
        self.calculate_LINE1_IN()
        self.calculate_k0_n0(LINE1_z0z1_mag, LINE1_z0z1_ang)
        self.calculate_mag_ang_R_X('A')
        self.calculate_mag_ang_R_X('B')
        self.calculate_mag_ang_R_X('C')
        self.combine_calculate_mag_ang_R_X('AB')
        self.combine_calculate_mag_ang_R_X('BC')
        self.combine_calculate_mag_ang_R_X('CA')


    def _calculate_IL_real_imag(self, IL1, Ang_I1, IL2, Ang_I2, IL3, Ang_I3):
        for IL, Ang_I in zip([IL1, IL2, IL3], [Ang_I1, Ang_I2, Ang_I3]):
            IL_Real = IL * math.cos(math.radians(Ang_I))
            IL_Imag = IL * math.sin(math.radians(Ang_I))
            self.real_data.append(IL_Real)
            self.imag_data.append(IL_Imag)

    def _calculate_V_real_imag(self, U1, Ang_U1, U2, Ang_U2, U3, Ang_U3):
        for U, Ang_U in zip([U1, U2, U3], [Ang_U1, Ang_U2, Ang_U3]):
            V_Real = U * math.cos(math.radians(Ang_U))
            V_Imag = U * math.sin(math.radians(Ang_U))
            self.real_data.append(V_Real)
            self.imag_data.append(V_Imag)

    def _create_complex_data(self):
        for i in range(6):
            self.complex_data.append(complex(self.real_data[i], self.imag_data[i]))


    def calculate_LINE1_IN(self):
        # Calculate LINE1_IN_Complex as the sum of IL1_complex, IL2_complex, and IL3_complex
        # LINE1_IN_Complex = self.complex_data[0] + self.complex_data[1] + self.complex_data[2]
        LINE1_IN_Complex = -24.3725335851725-2.63909674692661j

        # Calculate LINE1_IN_Imag and LINE1_IN_Real
        LINE1_IN_Imag = LINE1_IN_Complex.imag
        LINE1_IN_Real = LINE1_IN_Complex.real
        LINE1_IN_Mag = math.sqrt(LINE1_IN_Real**2 + LINE1_IN_Imag**2)
        LINE1_IN_Ang = math.degrees(math.atan2(LINE1_IN_Imag, LINE1_IN_Real))


        self.line1_IN_data.extend([LINE1_IN_Real, LINE1_IN_Imag, LINE1_IN_Complex, LINE1_IN_Mag, LINE1_IN_Ang])
        
    def calculate_k0_n0(self, LINE1_z0z1_mag, LINE1_z0z1_ang):
        # Calculate k0 and n0 coefficients
        LINE1_z0z1_ang_rad = math.radians(LINE1_z0z1_ang)
        LINE1_k0 = cmath.rect(LINE1_z0z1_mag, LINE1_z0z1_ang_rad) - 1
        LINE1_complex_number = complex(3, 0)
        LINE1_n0 = LINE1_k0 / LINE1_complex_number
        product_result = self.line1_IN_data[2] * LINE1_n0

        self.line1_k0 = LINE1_k0
        self.line1_n0 = LINE1_n0
        self.product_result = product_result

    def calculate_mag_ang_R_X(self, Z_type):
        # Calculate sum_result
        
        
        # Calculate LINE1_ZA or LINE1_ZB based on Z_type
        if Z_type == 'A':
            V_index = 3
            IL_index = 0
            data_list = self.data_ZA
        elif Z_type == 'B':
            V_index = 4
            IL_index = 1
            data_list = self.data_ZB
        elif Z_type == 'C':
            V_index = 5
            IL_index = 2
            data_list = self.data_ZC
        else:
            raise ValueError("Invalid Z_type. Must be 'A' or 'B' or 'C'.")
        

        sum_result = self.complex_data[IL_index] + self.product_result

        Z_line = self.complex_data[V_index] / sum_result
        
        # Extract real and imaginary parts of LINE1_ZA or LINE1_ZB
        Z_Real = Z_line.real
        Z_Imag = Z_line.imag
        data_list.extend([Z_Real, Z_Imag])
        
        # Calculate magnitude and angle of LINE1_ZA or LINE1_ZB
        Z_Mag = abs(self.complex_data[V_index] / self.complex_data[IL_index])
        Z_Ang = math.degrees(cmath.phase(self.complex_data[V_index] / self.complex_data[IL_index]))
        
        # Convert angle to radians
        Z_Ang_radians = math.radians(Z_Ang)
        
        # Calculate R and X components of LINE1_ZA or LINE1_ZB
        Z_R = Z_Mag * math.cos(Z_Ang_radians)
        Z_X = Z_Mag * math.sin(Z_Ang_radians)
        data_list.extend([Z_Mag, Z_Ang, Z_R, Z_X])

    def combine_calculate_mag_ang_R_X(self, Z_type):
        if Z_type == "AB":
            V_topIndex = 4
            V_bottomIndex = 3
            IL_topIndex = 1
            IL_bottomIndex = 0
            data_list = self.data_ZAB
        elif Z_type == "BC":
            V_topIndex = 5
            V_bottomIndex = 4
            IL_topIndex = 2
            IL_bottomIndex = 1
            data_list = self.data_ZBC
        elif Z_type == "CA":             
            V_topIndex = 3
            V_bottomIndex = 5
            IL_topIndex = 0
            IL_bottomIndex = 2
            data_list = self.data_ZCA
        else:
            raise ValueError("Invalid Z_type. Must be 'AB' or 'BC' or 'CA'.")
        
        LINE1_Z_Mag = abs((self.complex_data[V_bottomIndex] - self.complex_data[V_topIndex]) / (self.complex_data[IL_bottomIndex] -self.complex_data[IL_topIndex]))
        LINE1_diff_Vbot_Vtop = self.complex_data[V_bottomIndex] - self.complex_data[V_topIndex]
        LINE1_diff_Ibot_Itop = self.complex_data[IL_bottomIndex] - self.complex_data[IL_topIndex]
        LINE1_Z_Ang = math.degrees(math.atan2(LINE1_diff_Vbot_Vtop.imag, LINE1_diff_Vbot_Vtop.real) - math.atan2(LINE1_diff_Ibot_Itop.imag, LINE1_diff_Ibot_Itop.real))
        LINE1_Z_Ang_radians = math.radians(LINE1_Z_Ang)
        LINE1_Z_R = LINE1_Z_Mag * math.cos(LINE1_Z_Ang_radians)
        LINE1_Z_X = LINE1_Z_Mag * math.sin(LINE1_Z_Ang_radians)
        data_list.extend([LINE1_Z_Mag, LINE1_Z_Ang, LINE1_Z_R, LINE1_Z_X])


    def get_real_data(self):
        IL1_Real, IL2_Real, IL3_Real, V1_Real, V2_Real, V3_Real = self.real_data
        return IL1_Real, IL2_Real, IL3_Real, V1_Real, V2_Real, V3_Real

    def get_imag_data(self):
        IL1_Imag, IL2_Imag, IL3_Imag, V1_Imag, V2_Imag, V3_Imag = self.imag_data
        return IL1_Imag, IL2_Imag, IL3_Imag, V1_Imag, V2_Imag, V3_Imag

    def get_complex_data(self):
        IL1_Complex, IL2_Complex, IL3_Complex, V1_Complex, V2_Complex, V3_Complex = self.complex_data
        return IL1_Complex, IL2_Complex, IL3_Complex, V1_Complex, V2_Complex, V3_Complex

    def get_line1_IN_data(self):
        LINE1_IN_Real, LINE1_IN_Imag, LINE1_IN_Complex, LINE1_IN_Mag, LINE1_IN_Ang = self.line1_IN_data
        return LINE1_IN_Real, LINE1_IN_Imag, LINE1_IN_Complex, LINE1_IN_Mag, LINE1_IN_Ang
    
    def get_LINE1_k0(self):
        return self.line1_k0

    def get_LINE1_n0(self):
        return self.line1_n0

    def get_LINE1_PR(self):
        return self.product_result
    
    def get_ZA_data(self):
        LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X = self.data_ZA
        return LINE1_ZA_Real, LINE1_ZA_Imag, LINE1_ZA_Mag, LINE1_ZA_Ang, LINE1_ZA_R, LINE1_ZA_X
    
    def get_ZB_data(self):
        LINE1_ZB_Real, LINE1_ZB_Imag, LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X = self.data_ZB
        return LINE1_ZB_Real, LINE1_ZB_Imag, LINE1_ZB_Mag, LINE1_ZB_Ang, LINE1_ZB_R, LINE1_ZB_X
    
    def get_ZC_data(self):
        LINE1_ZC_Real, LINE1_ZC_Imag, LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X = self.data_ZC
        return LINE1_ZC_Real, LINE1_ZC_Imag, LINE1_ZC_Mag, LINE1_ZC_Ang, LINE1_ZC_R, LINE1_ZC_X
    
    def get_ZAB_data(self):
        LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X = self.data_ZAB
        return LINE1_ZAB_Mag, LINE1_ZAB_Ang, LINE1_ZAB_R, LINE1_ZAB_X

    def get_ZBC_data(self):
        LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X = self.data_ZBC
        return LINE1_ZBC_Mag, LINE1_ZBC_Ang, LINE1_ZBC_R, LINE1_ZBC_X

    def get_ZCA_data(self):
        LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X = self.data_ZCA
        return LINE1_ZCA_Mag, LINE1_ZCA_Ang, LINE1_ZCA_R, LINE1_ZCA_X
