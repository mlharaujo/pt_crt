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
    
    # Remove leading/trailing whitespace and return
    return s.strip()

def clean_headers(s):

    # Remove numbers inside parentheses, like (1) or (2,3)
    s = re.sub(r'\(\d+(?:,\d+)*\)', '', s)

    # Remove ".1" from the end
    s = re.sub(r'\.1$', '', s)
    
    # Remove leading/trailing whitespace and return
    return s.strip() 

def pre_process(df):
    df.rename(index=clean_index, inplace=True)
    df.reset_index(inplace=True)
    df.rename(columns={'index' : 'Category/Fuel'},inplace=True)
    df.replace({"CO2" : "NO\"", "CH4" : "NO\"", "N2O" : "NO\""}, "NO", inplace=True)

def correct_code(code):
    if code[-1:] != '.':
        code = code + '.'
    return code

#This reads the relevant rows and columns in each of the five tables from the file into dataframes, does some cleaning and concatenates into one dataframe
def read_and_process(file_path):
    
    s1 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s1",
                   index_col=0,
                   usecols="B,H:J",
                   skiprows=[0,1,2,3,4,5,6,8],
                   nrows=49
                   )
    s1.rename(columns=clean_headers, inplace=True)

  
    s2 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s2",
                   index_col=0,
                   usecols="B,H:J",
                   skiprows=[0,1,2,3,4,5,6,8],
                   nrows=121
                   )   
    s2.rename(columns=clean_headers, inplace=True)
    s2.rename(index={'Rubber': '1.A.2.g.viii.x. Rubber',
                 'Other Transformation Industry': '1.A.2.g.viii.y. Other Transformation Industry'
                },
          inplace=True)

    s3 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s3",
                   index_col=0,
                   usecols="B,H:J",
                   skiprows=[0,1,2,3,4,5,6,8,55],
                   nrows=79
                   )
    s3.rename(columns=clean_headers, inplace=True)
    s3.rename(index={'Lubricant Oil' : 'Other liquid fuels: lubricant oil'}, inplace=True)

    s4 = pd.read_excel(file_path,
                   sheet_name="Table1.A(a)s4",
                   index_col=0,
                   usecols="B,H:J",
                   skiprows=[0,1,2,3,4,5,6,8],
                   nrows=92)
    s4.rename(columns=clean_headers, inplace=True)
    s4.rename(index={'Military aviation' : '1.A.5.b.i. Military aviation'}, inplace=True)

    s5 = pd.read_excel(file_path,
                   sheet_name="Table1.D",
                   index_col=0,
                   usecols="B,G:I",
                   skiprows=[0,1,2,3,4,5,6,8],
                   nrows=13
                   )
    s5.rename(columns=clean_headers, inplace=True)    
    s5.rename_axis(index=None, inplace=True)

    result = pd.concat([s1,s2,s3,s4,s5])

    pre_process(result) 

    return result

#takes a dataframe (containing the relevant contents from a file) and the corresponding year and accumulates the rows into a list of data
def accumulate(data, df, year: int):
    (category_code, category_name, fuel) = ('','','')
    for i in df.index:
        category_fuel = df["Category/Fuel"][i] 
        
        if is_category(category_fuel):
            (category_code, category_name) = category_fuel.split(' ', maxsplit=1)
            category_code = correct_code(category_code)
            
            fuel = "All fuels except biomass"
        else:
            fuel = category_fuel
    
        for gas in ["CO2", "CH4", "N2O"]:
        
            data.append({"Year" : year,
                         "Category code" : category_code,
                         "Category name" : category_name,
                         "Fuel" : fuel,
                         "Gas" : gas,
                         "Units": "kt",
                         "Value" : df[gas][i]})

folder = "prt-crt-2025-v0.6-20250314-152459_started\\"
year = 1990
data = []

for file in os.listdir(os.fsencode("prt-crt-2025-v0.6-20250314-152459_started")):
    
    file_path = folder + os.fsdecode(file)
    df = read_and_process(file_path)
    accumulate(data, df, year)
    year = year + 1
    
df = pd.DataFrame(data)
df.to_csv("prt_crt_2025_fuel_combustion.csv", index=False)
