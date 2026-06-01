import pandas as pd
import re
import os

def is_category(s):
    return s[:1].isdigit()

def clean_index(s):
    # Remove numbers inside parentheses, like (1)
    s = re.sub(r'\(\d+\)', '', s)

    # Remove "(please specify)"
    s = re.sub(r'\(please specify\)', '', s)

    # Replace whitespace of any lenth by a single space
    s = re.sub(r'\s+', ' ', s)

    # Remove spaces inside the category codes
    s = re.sub(r'\s+(\w)\.', r'\1.' ,s )
    
    # Remove leading/trailing whitespace and return
    return s.strip()


def pre_process(df):
    df.rename(index=clean_index, inplace=True)
    df.replace("NO\"", "NO", inplace=True)
    df.reset_index(inplace=True)
    
def correct_code(code):
    code = re.sub(r'\s+', '', code)
    
    if code[-1:] != '.':
        code = code + '.'
        
    return code

def one_A_s1(file_path):
    
    one_A_s1 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s1",
                   index_col=0,
                   usecols="B,H:K",
                   names=["Category/Fuel", "CO2 Emissions", "CH4 Emissions", "N2O Emissions", "CO2 Captured"],
                   skiprows=[0,1,2,3,4,5,6,7],
                   nrows=49
                   )
    
    return one_A_s1

def one_A_s2(file_path):

    one_A_s2 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s2",
                   index_col=0,
                   usecols="B,H:K",
                   names=["Category/Fuel", "CO2 Emissions", "CH4 Emissions", "N2O Emissions", "CO2 Captured"],
                   skiprows=[0,1,2,3,4,5,6,7],
                   nrows=121
                   )

    one_A_s2.rename(index={'Rubber': '1.A.2.g.viii.x. Rubber',
                       'Other Transformation Industry': '1.A.2.g.viii.y. Other Transformation Industry'},
                inplace=True)

    return one_A_s2

def one_A_s3(file_path):

    one_A_s3 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s3",
                   index_col=0,
                   usecols="B,H:J",
                   names=["Category/Fuel", "CO2 Emissions", "CH4 Emissions", "N2O Emissions"],
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
                   names=["Category/Fuel", "CO2 Emissions", "CH4 Emissions", "N2O Emissions", "CO2 Captured"],
                   skiprows=[0,1,2,3,4,5,6,7],
                   nrows=92)
    one_A_s4.rename(index={'Military aviation' : '1.A.5.b.i. Military aviation'}, inplace=True)

    return one_A_s4

def one_D(file_path):
    
    one_D = pd.read_excel(file_path,
                   sheet_name="Table1.D",
                   index_col=0,
                   usecols="B,G:I",
                   names=["Category/Fuel", "CO2 Emissions", "CH4 Emissions", "N2O Emissions"],
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
                        names=["Category/Fuel", "CH4 Emissions", "CO2 Emissions", "CH4 Recovery/Flaring", "CO2 Recovery/Flaring"],
                        nrows=13
                   )

    return one_B_1

def one_B_2(file_path):

    one_B_2 = pd.read_excel(file_path,
                   sheet_name="Table1.B.2",
                   index_col=0,
                   skiprows=[0,1,2,3,4,5,6,7],
                   usecols="B,I:L",
                   names=["Category/Fuel", "CO2 Emissions", "CH4 Emissions", "N2O Emissions", "CO2 Recovery"],
                   nrows=25
                   )
    one_B_2.rename(index={'Geothermal' : '1.B.2.d.i Geothermal'}, inplace=True)


    return one_B_2

#This reads the relevant rows and columns in each of the sheets from the file into dataframes, does some cleaning and returns a list of dataframes
def read_and_process(file_path):

    dfs = []
    for sheet in sheets:
        df = sheet(file_path)
        pre_process(df)
        dfs.append(df)

    return dfs

#takes a dataframe (containing the relevant contents from a sheet) and the corresponding year and accumulates the rows into a list of data
def accumulate(data, df, year: int):

    for i in df.index:
        category_fuel = df["Category/Fuel"][i]
        if is_category(category_fuel):
            (category_code, category_name) = category_fuel.split(' ', maxsplit=1)
            category_code = correct_code(category_code)

            if category_code.startswith("1.A") or category_code.startswith("1.D"):
                fuel = "All fuels except biomass"
            else:
                fuel = "NA"
        else:
            fuel = category_fuel
    
        for gas_type in df.columns[1:]:

            (gas, type) = gas_type.split(' ', maxsplit=1)
            
            data.append({"Year" : year, 
                         "Category code" : category_code, 
                         "Category name" : category_name, 
                         "Fuel" : fuel, 
                         "Gas" : gas,
                         "Type": type,
                         "Units": "kt", 
                         "Value" : df[gas_type][i]})

folder = "PRT-CRT-2026-V1.0"
year = 1990
data = []
sheets = [one_A_s1, one_A_s2, one_A_s3, one_B_1, one_B_2, one_D]

for file in os.listdir(os.fsencode(folder)):
    
    file_path = folder + "\\" + os.fsdecode(file)
    dfs = read_and_process(file_path)
    for df in dfs:
        accumulate(data, df, year)
    year = year + 1

    
df = pd.DataFrame(data)
df.to_csv("prt_crt_2026.csv", index=False)
