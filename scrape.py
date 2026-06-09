import pandas as pd
import re
import os

# Detects whether str is a valid depth n segment of a category code
def is_level(str, n):
    if n == 1:
        return re.fullmatch(r'[1-5]',str)
    elif n == 2:
        return re.fullmatch(r'[A-J]', str)
    elif n == 3:
        return re.fullmatch(r'[1-9]', str) or str == "10" 
    elif n == 4:
        return re.fullmatch(r'[a-h]', str)
    elif n == 5:
        return str in ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
    elif n == 6:
        return re.fullmatch(r'[a-h]', str)

# Detects whether first and second are valid consecutive sections of a category code
# e.g. (1, A) , (A, 1) , (1, a) , (a, i), (i, a) are all valid
def is_next(first, second):

    for i in range(1,6):

        if is_level(first, i) and is_level(second, i+1):
            return True

    return False

# Takes a label and returns it in correct format, e.g.
# "1. A .1.b Petroleum    refining" -> "1.A.1.b. Petroleum refining"
def code_name(label):
            
    segments = [segment.strip() for segment in label.split('.')]
    
    # This is the case where we get only a name, with no code
    if len(segments) == 1:
        return ' '.join(label.split())

    # the stuff between the last two "." 
    last = segments[-2]

    # everything after the last "."
    after = segments[-1].split()

    # the case where the code continues after the last "." e.g. "1.A.2 Manufacturing industries and construction"
    if is_next(last, after[0]):
        code = '.'.join(segments[:-1]) + '.' + after[0] + '.'
        name = ' '.join(after[1:])
    # the case where the last "." marks the end of the code, as it should, e.g. "1.A.1. Energy industries"
    else:
        code = '.'.join(segments[:-1]) + '.'
        name = ' '.join(after)
        
    return " ".join([code, name])

# This is applied to all indices for cleanup
def clean_index(s):
    # Remove numbers inside parentheses, like (1)
    s = re.sub(r'\(\d+\)', '', s)

    # Remove "(please specify)"
    s = re.sub(r'\(please specify\)', '', s)

    # Fix format
    s = code_name(s)

    return s

#Cleanup and reset indices to 1,2,3,...
def pre_process(df):
    df.rename(index=clean_index, inplace=True)
    df.replace("NO\"", "NO", inplace=True)
    df.reset_index(inplace=True)

# The first child code of a given category code
def first_child(parent):
    depth = len(parent.split('.'))
    suffixes = ['1.','A.','1.','a.','i.','a.']
    return parent + suffixes[depth-1]

# The code that follows a given category code
def next_code(code):
    list = code.split('.')
    depth = len(list) - 1
    list[-2] = next(list[-2], depth)
    
    return '.'.join(list)

# The code segment that follows a given code segment
def next(segment, depth):
    if depth == 5:
        return next_roman_numeral(segment)
    else:
        return  chr(ord(segment) + 1)

def next_roman_numeral(numeral):
    if numeral == 'i':
        return 'ii'
    if numeral == 'ii':
        return 'iii'
    if numeral == 'iii':
        return 'iv'
    if numeral == 'iv':
        return 'v'
    if numeral == 'v':
        return 'vi'
    if numeral == 'vi':
        return 'vii'
    if numeral == 'vii':
        return 'viii'
    if numeral == 'viii':
        return 'ix'
    if numeral == 'ix':
        return 'x'

# Goes through entries in a dataframe and adds missing category codes to the entries in the "Category/Fuel" column
# To be applied only when this column consists exclusively of categories, not fuels

def add_missing_codes(df):

    i = 0
    entries = df["Category/Fuel"]
    len = entries.size

    while i < len:
        # Skip entries that already have a code
        while i < len:
            entry = entries[i]
            if not entry[:1].isdigit():
                break
            i = i + 1

        # Deal with first entry in a consecutive block of entries without code
        previous = entries[i-1]
        parent_code = previous.split(maxsplit=1)[0]
        code = first_child(parent_code)
        df.loc[i, "Category/Fuel"] = code + ' ' +  entry
        i = i + 1

        # Deal with remaining entries in a consecutive block of entries without code
        while i < len:
            entry = entries[i]
            if entry[:1].isdigit():
                break
            code = next_code(code)
            df.loc[i, "Category/Fuel"] = code + ' ' +  entry
            i = i + 1


# Check if a string starts with a digit
# We will use it in a context where this implies it must consist of a category code and name
def is_category(s):
    return s[:1].isdigit()

def one_A_s1(file_path):
    
    one_A_s1 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s1",
                   index_col=0,
                   usecols="B,H:K",
                   names=["Category/Fuel", "CO2,Emissions", "CH4,Emissions", "N2O,Emissions", "CO2,Captured"],
                   skiprows=[0,1,2,3,4,5,6,7],
                   nrows=49
                   )
    
    return one_A_s1

def one_A_s2(file_path):

    one_A_s2 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s2",
                   index_col=0,
                   usecols="B,H:K",
                   names=["Category/Fuel", "CO2,Emissions", "CH4,Emissions", "N2O,Emissions", "CO2,Captured"],
                   skiprows=[0,1,2,3,4,5,6,7],
                   nrows=121
                   )

    one_A_s2.rename(index={'Rubber': '1.A.2.g.viii.a. Rubber',
                       'Other Transformation Industry': '1.A.2.g.viii.b. Other Transformation Industry'},
                inplace=True)

    return one_A_s2

def one_A_s3(file_path):

    one_A_s3 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s3",
                   index_col=0,
                   usecols="B,H:J",
                   names=["Category/Fuel", "CO2,Emissions", "CH4,Emissions", "N2O,Emissions"],
                   skiprows=[0,1,2,3,4,5,6,7,55],
                   nrows=79
                   )
    one_A_s3.rename(index={'Lubricant Oil' : 'Other liquid fuels: lubricant oil'}, inplace=True)

    return one_A_s3

def one_A_s4(file_path):

    one_A_s4 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s4",
                   index_col=0,
                   usecols="B,H:K",
                   names=["Category/Fuel", "CO2,Emissions", "CH4,Emissions", "N2O,Emissions", "CO2,Captured"],
                   skiprows=[0,1,2,3,4,5,6,7],
                   nrows=92)
    one_A_s4.rename(index={'Military aviation' : '1.A.5.b.i. Military aviation'}, inplace=True)

    return one_A_s4

def one_D(file_path):
    
    one_D = pd.read_excel(file_path,
                   sheet_name="Table1.D",
                   index_col=0,
                   usecols="B,G:I",
                   names=["Category/Fuel", "CO2,Emissions", "CH4,Emissions", "N2O,Emissions"],
                   skiprows=[0,1,2,3,4,5,6,7],
                   nrows=13
                   )

    return one_D

def one_B_1(file_path):

    one_B_1 = pd.read_excel(file_path,
                        sheet_name="Table1.B.1",
                        index_col=0,
                        skiprows=[0,1,2,3,4,5,6,7],
                        usecols="B,F:I",
                        names=["Category/Fuel", "CH4,Emissions", "CO2,Emissions", "CH4,Recovery/Flaring", "CO2,Recovery/Flaring"],
                        nrows=13
                   )

    return one_B_1

def one_B_2(file_path):

    one_B_2 = pd.read_excel(file_path,
                   sheet_name="Table1.B.2",
                   index_col=0,
                   skiprows=[0,1,2,3,4,5,6,7],
                   usecols="B,I:L",
                   names=["Category/Fuel", "CO2,Emissions", "CH4,Emissions", "N2O,Emissions", "CO2,Recovery"],
                   nrows=25
                   )

    return one_B_2

def one_C(file_path):

    one_C = pd.read_excel(file_path,
                   sheet_name="Table1.C",
                   index_col=0,
                   skiprows=[0,1,2,3,4,5,6,7],
                   usecols="B,E",
                   names=["Category/Fuel", "CO2,Emissions"],
                   nrows=8
                   )

    return one_C

def two_I_AH(file_path):

    two_I_AH = pd.read_excel(file_path,
                   sheet_name="Table2(I).A-H",
                   index_col=0,
                   skiprows=[0,1,2,3,4,5,6,7],
                   usecols="B,H:N",
                   names=["Category/Fuel",
                          "CO2,Emissions",
                          "CH4,Emissions",
                          "N2O,Emissions",
                          "Fossil CO2,Recovery/Capture",
                          "Biogenic CO2,Recovery/Capture",
                          "CH4,Recovery/Capture",
                          "N2O,Recovery/Capture"],
                   nrows=91
                   )

    return two_I_AH

#This reads the relevant rows and columns in each of the sheets from the file into dataframes, does some cleaning and returns a list of dataframes
def read_and_process(file_path):

    dfs = []
    for sheet in sheets:
        
        df = sheet(file_path)
        pre_process(df)

        # For combustion categories we already added missing codes by hand, as it's difficult to distinguish categories from fuels before we have codes. 
        if sheet not in combustion:
            add_missing_codes(df)

        dfs.append(df)

    return dfs

#takes a dataframe (containing the relevant contents from a sheet) and the corresponding year and accumulates the rows into a list of data
def accumulate(data, df, year: int):

    for i in df.index:
        category_fuel = df["Category/Fuel"][i]
        if is_category(category_fuel):
            (category_code, category_name) = category_fuel.split(maxsplit=1)

            if category_code.startswith("1.A") or category_code.startswith("1.D"):
                fuel = "All fuels except biomass"
            else:
                fuel = "NA"
        else:
            fuel = category_fuel
    
        for gas_type in df.columns[1:]:

            (gas, type) = gas_type.split(',', maxsplit=1)
            
            data.append({"Year" : year, 
                         "Category code" : category_code, 
                         "Category name" : category_name, 
                         "Fuel" : fuel, 
                         "Gas" : gas,
                         "Type": type,
                         "Units": "kt", 
                         "Value" : df[gas_type][i]})

# Start of script

folder = "PRT-CRT-2026-V1.0"
year = 1990
data = []
combustion = [one_A_s1, one_A_s2, one_A_s3, one_A_s4, one_D]
others = [one_B_1, one_B_2, one_C, two_I_AH]
sheets = combustion + others

for file in os.listdir(os.fsencode(folder)):
    
    file_path = folder + "\\" + os.fsdecode(file)
    dfs = read_and_process(file_path)
    for df in dfs:
        accumulate(data, df, year)
    year = year + 1
    
df = pd.DataFrame(data)
df.to_csv("prt_crt_2026.csv", index=False)
