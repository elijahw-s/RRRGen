import os

def find_closest_value(K, lst):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]

def find_h2o_temp_K_density(K):
    try:
        C = float('{:.2f}'.format(float(K)-273.15))
        density = float('{:.6f}'.format((
            999.83952
            +16.945176*C
            -7.9870401e-3*C**2
            -46.170461e-6*C**3
            +105.56302e-9*C**4
            -280.54253e-12*C**5)/(1+16.897850e-3*C)/1000))
        # print(f"\n   comment. at {C} C, h2o density was calculated to be {density} g/cc ")
        # Equation for water density given temperature in C, works for 0 to 150 C at 1 atm
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4909168/

        if C < 0 or C > 150: 
            print(f"\n   warning. h2o has calculated density {density} g/cc at given temp {C} C")
            print(f"   warning. but that is outside the range 0 - 150 C safely predicted by the formula ")
        return density

    except:
        print(f"\n   fatal. finding h2o density for temperature {K} K failed")
        print(f"   fatal. ensure you are inputing a numeric-only str, float, or int into the function")

def find_available_name(name):
    '''
    Finds first available file path
    '''
    fileNo = 1
    while True:
        testName = f'{name}_{fileNo}'
        if not os.path.exists(f'{testName}.i'):
            return testName
        else:
            fileNo += 1

def make_cs(num):
    return 'c\n' * num

def k_to_mev(k):
    return 1.380649/1.602176634*10**-10*k