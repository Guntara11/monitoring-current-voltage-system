import math
import utils
import pymongo
from utils import ZoneCalculation



client = pymongo.MongoClient("mongodb+srv://sopiand23:Manusiakuat1@mycluster.bfapaaq.mongodb.net/?retryWrites=true&w=majority")
db = client["MyData"]
collection = db["Params"]

# Define the filter to retrieve data for "Line_1"
choice = input("select line :")

if choice == '1':
    filter_query = {"_id": "Line_1"}
elif choice == '2':
    filter_query = {"_id": "Line_2"}
elif choice == '3':
    filter_query = {"_id": "Line_3"}
elif choice == '4':
    filter_query = {"_id": "Line_4"}
elif choice == '5':
    filter_query = {"_id": "Line_5"}
elif choice == '6':
    filter_query = {"_id": "Line_6"}
elif choice == '7':
    filter_query = {"_id": "Line_7"}
elif choice == '8':
    filter_query = {"_id": "Line_8"}
elif choice == '9':
    filter_query = {"_id": "Line_9"}
elif choice == '10':
    filter_query = {"_id": "Line_10"}
elif choice == '11':
    filter_query = {"_id": "Line_11"}
elif choice == '12':
    filter_query = {"_id": "Line_12"}
elif choice == '13':
    filter_query = {"_id": "Line_13"}
elif choice == '14':
    filter_query = {"_id": "Line_14"}
elif choice == '15':
    filter_query = {"_id": "Line_15"}
elif choice == '16':
    filter_query = {"_id": "Line_16"}
# Perform the query to retrieve the document
result = collection.find_one(filter_query)

# Print the result
print(result)


# LINE1_xpz1 = result['xpz1']
# LINE1_xpz2 = result['xpz2']
# LINE1_xpz3 = result['xpz3']

# LINE1_rpz1 = result['rpz1']
# LINE1_rpz2 = result['rpz2']
# LINE1_rpz3 = result['rpz3']

# LINE1_xgz1 = result['xgz1']
# LINE1_xgz2 = result['xgz2']
# LINE1_xgz3 = result['xgz3']

# LINE1_rgz1 = result['rgz1']
# LINE1_rgz2 = result['rgz2']
# LINE1_rgz3 = result['rgz3']

# LINE1_angle= result['angle']

# LINE1_z0z1_mag = result['z0z1_mag']
# LINE1_z0z1_ang = result['z0z1_ang']


LINE1_z0z1_mag = 6.181
LINE1_z0z1_ang = -2.55

LINE1_xpz1 = 12.6875
LINE1_xpz2 = 19
LINE1_xpz3 = 25.375

LINE1_rpz1 = 17.3125
LINE1_rpz2 = 26
LINE1_rpz3 = 34.625

LINE1_xgz1 = 12.6875
LINE1_xgz2 = 19
LINE1_xgz3 = 25.375

LINE1_rgz1 = 46.1875
LINE1_rgz2 = 46.1875
LINE1_rgz3 = 46.1875

LINE1_angle= 75

LINE1_z0z1_mag = 6.181
LINE1_z0z1_ang = -2.55


zone_calc = ZoneCalculation()

zone_calc.calculate_values(LINE1_xpz1, LINE1_xpz2, LINE1_xpz3, LINE1_rpz1, LINE1_rpz2, LINE1_rpz3,
                     LINE1_xgz1, LINE1_xgz2, LINE1_xgz3, LINE1_rgz1, LINE1_rgz2, LINE1_rgz3, LINE1_angle, LINE1_z0z1_mag,
                     LINE1_z0z1_ang)

################################# PHASE TO GROUND ################################################
# Getting the real and imaginary data
LINE1_Z1_PG_Real, LINE1_Z2_PG_Real, LINE1_Z3_PG_Real =  zone_calc.get_PG_real_data()
pg_LINE1_reach_z1_x, pg_LINE1_reach_z2_x, pg_LINE1_reach_z3_x = LINE1_Z1_PG_Real, LINE1_Z2_PG_Real, LINE1_Z3_PG_Real

LINE1_Z1_PG_Imag, LINE1_Z2_PG_Imag, LINE1_Z3_PG_Imag = zone_calc.get_PG_imag_data()
pg_LINE1_reach_z1_y, pg_LINE1_reach_z2_y, pg_LINE1_reach_z3_y = LINE1_Z1_PG_Imag, LINE1_Z2_PG_Imag, LINE1_Z3_PG_Imag

pg_top_right_z1_x, pg_top_right_z2_x, pg_top_right_z3_x =  zone_calc.get_tr_pg_x()

pg_top_right_z1_y= pg_LINE1_reach_z1_y
pg_top_right_z2_y= pg_LINE1_reach_z2_y
pg_top_right_z3_y= pg_LINE1_reach_z3_y

pg_top_left_z1_x= LINE1_Z1_PG_Real-(0.5*LINE1_rgz1)
pg_top_left_z1_y= pg_LINE1_reach_z1_y
pg_top_left_z2_x= LINE1_Z2_PG_Real-(0.5*LINE1_rgz2)
pg_top_left_z2_y= pg_LINE1_reach_z2_y
pg_top_left_z3_x= LINE1_Z3_PG_Real-(0.5*LINE1_rgz3)
pg_top_left_z3_y= pg_LINE1_reach_z3_y



pg_down_right_z1_x, pg_down_right_z2_x, pg_down_right_z3_x = zone_calc.get_dr_pg_x()
pg_down_right_z1_y, pg_down_right_z2_y, pg_down_right_z3_y = zone_calc.get_dr_pg_y()


pg_down_left_z1_x= -0.5 * pg_down_right_z1_x
pg_down_left_z1_y= 0.5 * abs(pg_down_right_z1_y)
pg_down_left_z2_x= -0.5 * pg_down_right_z2_x
pg_down_left_z2_y= 0.5 * abs(pg_down_right_z2_y)
pg_down_left_z3_x= -0.5 * pg_down_right_z3_x
pg_down_left_z3_y= 0.5 * abs(pg_down_right_z2_y)

pg_right_side_z1_x= pg_top_right_z1_x
pg_right_side_z1_y= pg_LINE1_reach_z1_y
pg_right_side_z2_x= pg_top_right_z2_x
pg_right_side_z2_y= pg_LINE1_reach_z2_y
pg_right_side_z3_x= pg_top_right_z3_x
pg_right_side_z3_y= pg_LINE1_reach_z3_y

pg_left_side_z1_x= pg_down_left_z1_x
pg_left_side_z1_y= pg_down_left_z1_y
pg_left_side_z2_x= pg_down_left_z2_x
pg_left_side_z2_y= pg_down_left_z1_y
pg_left_side_z3_x= pg_down_left_z3_x
pg_left_side_z3_y= pg_down_left_z1_y

################################# PHASE TO PHASE ################################################

# Getting the real and imaginary data
LINE1_Z1_PP_Real, LINE1_Z2_PP_Real, LINE1_Z3_PP_Real =  zone_calc.get_PP_real_data()
pp_LINE1_reach_z1_x, pp_LINE1_reach_z2_x, pp_LINE1_reach_z3_x = LINE1_Z1_PP_Real, LINE1_Z2_PP_Real, LINE1_Z3_PP_Real

LINE1_Z1_PP_Imag, LINE1_Z2_PP_Imag, LINE1_Z3_PP_Imag = zone_calc.get_PP_imag_data()
pp_LINE1_reach_z1_y, pp_LINE1_reach_z2_y, pp_LINE1_reach_z3_y = LINE1_Z1_PP_Imag, LINE1_Z2_PP_Imag, LINE1_Z3_PP_Imag

pp_top_right_z1_x, pp_top_right_z2_x, pp_top_right_z3_x =  zone_calc.get_tr_pp_x()


pp_top_right_z1_y= pp_LINE1_reach_z1_y
pp_top_right_z2_y= pp_LINE1_reach_z2_y
pp_top_right_z3_y= pp_LINE1_reach_z3_y

pp_top_left_z1_x= LINE1_Z1_PP_Real-(0.5*LINE1_rpz1)
pp_top_left_z1_y= pp_LINE1_reach_z1_y
pp_top_left_z2_x= LINE1_Z2_PP_Real-(0.5*LINE1_rpz2)
pp_top_left_z2_y= pp_LINE1_reach_z2_y
pp_top_left_z3_x= LINE1_Z3_PP_Real-(0.5*LINE1_rpz3)
pp_top_left_z3_y= pp_LINE1_reach_z3_y

pp_down_right_z1_x, pp_down_right_z2_x, pp_down_right_z3_x = zone_calc.get_dr_pp_x()
pp_down_right_z1_y, pp_down_right_z2_y, pp_down_right_z3_y = zone_calc.get_dr_pp_y()

pp_down_left_z1_x= -0.5 * pp_down_right_z1_x
pp_down_left_z1_y= 0.5 * abs(pp_down_right_z1_y)
pp_down_left_z2_x= -0.5 * pp_down_right_z2_x
pp_down_left_z2_y= 0.5 * abs(pp_down_right_z2_y)
pp_down_left_z3_x= -0.5 * pp_down_right_z3_x
pp_down_left_z3_y= 0.5 * abs(pp_down_right_z3_y)

pp_right_side_z1_x= pp_top_right_z1_x
pp_right_side_z1_y= pp_LINE1_reach_z1_y
pp_right_side_z2_x= pp_top_right_z2_x
pp_right_side_z2_y= pp_LINE1_reach_z2_y
pp_right_side_z3_x= pp_top_right_z3_x
pp_right_side_z3_y= pp_LINE1_reach_z3_y

pp_left_side_z1_x= pp_down_left_z1_x
pp_left_side_z1_y= pp_down_left_z1_y
pp_left_side_z2_x= pp_down_left_z2_x
pp_left_side_z2_y= pp_down_left_z1_y
pp_left_side_z3_x= pp_down_left_z3_x
pp_left_side_z3_y= pp_down_left_z1_y







# Printing the results
print("Phase to Ground:")
print("LINE1_Z1_PG_Real:", LINE1_Z1_PG_Real)
print("LINE1_Z2_PG_Real:", LINE1_Z2_PG_Real)
print("LINE1_Z3_PG_Real:", LINE1_Z3_PG_Real)
print("LINE1_Z1_PG_Imag:", LINE1_Z1_PG_Imag)
print("LINE1_Z2_PG_Imag:", LINE1_Z2_PG_Imag)
print("LINE1_Z3_PG_Imag:", LINE1_Z3_PG_Imag)

print("LINE1_reach_z1_x:", pg_LINE1_reach_z1_x)
print("LINE1_reach_z1_y:", pg_LINE1_reach_z1_y)
print("LINE1_reach_z2_x:", pg_LINE1_reach_z2_x)
print("LINE1_reach_z2_y:", pg_LINE1_reach_z2_y)
print("LINE1_reach_z3_x:", pg_LINE1_reach_z3_x)
print("LINE1_reach_z3_y:", pg_LINE1_reach_z3_y)

print("top_right_z1_x:", pg_top_right_z1_x)
print("top_right_z1_y:", pg_top_right_z1_y)
print("top_right_z2_x:", pg_top_right_z2_x)
print("top_right_z2_y:", pg_top_right_z2_y)
print("top_right_z3_x:", pg_top_right_z3_x)
print("top_right_z3_y:", pg_top_right_z3_y)

print("top_left_z1_x:", pg_top_left_z1_x)
print("top_left_z1_y:", pg_top_left_z1_y)
print("top_left_z2_x:", pg_top_left_z2_x)
print("top_left_z2_y:", pg_top_left_z2_y)
print("top_left_z3_x:", pg_top_left_z3_x)
print("top_left_z3_y:", pg_top_left_z3_y)

print("down_right_z1_x:", pg_down_right_z1_x)
print("down_right_z1_y:", pg_down_right_z1_y)
print("down_right_z2_x:", pg_down_right_z2_x)
print("down_right_z2_y:", pg_down_right_z2_y)
print("down_right_z3_x:", pg_down_right_z3_x)
print("down_right_z3_y:", pg_down_right_z3_y)


print("down_left_z1_x:", pg_down_left_z1_x)
print("down_left_z1_y:", pg_down_left_z2_y)
print("down_left_z2_x:", pg_down_left_z2_x)
print("down_left_z2_y:", pg_down_left_z2_y)
print("down_left_z3_x:", pg_down_left_z3_x)
print("down_left_z3_y:", pg_down_left_z3_y)


print("right_side_z1_x:", pg_right_side_z1_x)
print("right_side_z1_y:", pg_right_side_z1_y)
print("right_side_z2_x:", pg_right_side_z2_x)
print("right_side_z2_y:", pg_right_side_z2_y)
print("right_side_z3_x:", pg_right_side_z3_x)
print("right_side_z3_y:", pg_right_side_z3_y)

print("left_side_z1_x:", pg_left_side_z1_x)
print("left_side_z1_y:", pg_left_side_z1_y)
print("left_side_z2_x:", pg_left_side_z2_x)
print("left_side_z2_y:", pg_left_side_z2_y)
print("left_side_z3_x:", pg_left_side_z3_x)
print("left_side_z3_y:", pg_left_side_z3_y)



print("\n\n\nPhase to phase:")
print("LINE1_Z1_pp_Real:", LINE1_Z1_PP_Real)
print("LINE1_Z2_pp_Real:", LINE1_Z2_PP_Real)
print("LINE1_Z3_pp_Real:", LINE1_Z3_PP_Real)
print("LINE1_Z1_pp_Imag:", LINE1_Z1_PP_Imag)
print("LINE1_Z2_pp_Imag:", LINE1_Z2_PP_Imag)
print("LINE1_Z3_pp_Imag:", LINE1_Z3_PP_Imag)

print("LINE1_reach_z1_x:", pp_LINE1_reach_z1_x)
print("LINE1_reach_z1_y:", pp_LINE1_reach_z1_y)
print("LINE1_reach_z2_x:", pp_LINE1_reach_z2_x)
print("LINE1_reach_z2_y:", pp_LINE1_reach_z2_y)
print("LINE1_reach_z3_x:", pp_LINE1_reach_z3_x)
print("LINE1_reach_z3_y:", pp_LINE1_reach_z3_y)

print("top_right_z1_x:", pp_top_right_z1_x)
print("top_right_z1_y:", pp_top_right_z1_y)
print("top_right_z2_x:", pp_top_right_z2_x)
print("top_right_z2_y:", pp_top_right_z2_y)
print("top_right_z3_x:", pp_top_right_z3_x)
print("top_right_z3_y:", pp_top_right_z3_y)

print("top_left_z1_x:", pp_top_left_z1_x)
print("top_left_z1_y:", pp_top_left_z1_y)
print("top_left_z2_x:", pp_top_left_z2_x)
print("top_left_z2_y:", pp_top_left_z2_y)
print("top_left_z3_x:", pp_top_left_z3_x)
print("top_left_z3_y:", pp_top_left_z3_y)

print("down_right_z1_x:", pp_down_right_z1_x)
print("down_right_z1_y:", pp_down_right_z1_y)
print("down_right_z2_x:", pp_down_right_z2_x)
print("down_right_z2_y:", pp_down_right_z2_y)
print("down_right_z3_x:", pp_down_right_z3_x)
print("down_right_z3_y:", pp_down_right_z3_y)


print("down_left_z1_x:", pp_down_left_z1_x)
print("down_left_z1_y:", pp_down_left_z1_y)
print("down_left_z2_x:", pp_down_left_z2_x)
print("down_left_z2_y:", pp_down_left_z2_y)
print("down_left_z3_x:", pp_down_left_z3_x)
print("down_left_z3_y:", pp_down_left_z3_y)


print("right_side_z1_x:", pp_right_side_z1_x)
print("right_side_z1_y:", pp_right_side_z1_y)
print("right_side_z2_x:", pp_right_side_z2_x)
print("right_side_z2_y:", pp_right_side_z2_y)
print("right_side_z3_x:", pp_right_side_z3_x)
print("right_side_z3_y:", pp_right_side_z3_y)

print("left_side_z1_x:", pp_left_side_z1_x)
print("left_side_z1_y:", pp_left_side_z1_y)
print("left_side_z2_x:", pp_left_side_z2_x)
print("left_side_z2_y:", pp_left_side_z2_y)
print("left_side_z3_x:", pp_left_side_z3_x)
print("left_side_z3_y:", pp_left_side_z3_y)