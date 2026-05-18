After extracting the .7z file (source: https://apambiente.pt/sites/default/files/_Clima/Inventarios/20250509/prt-crt-2025-v0.6-20250314-152459_started.7z), one should have a folder containing 34 .xlsx files (corresponding to years 1990 - 2023), called "prt-crt-2025-v0.6-20250314-152459_started". 

Running the python script scrape.py from the directory containing this folder will produce a .csv file (prt_crt_2025_fuel_combustion.csv) containing all greenhouse gas (GHG) emissions data from the sheets "Table1.A(a)s1", "Table1.A(a)s2", "Table1.A(a)s3", "Table1.A(a)s4" and "Table1.D" in each of the 34 files.

This consists of all GHG emissions from fuel combustion reported by Portugal, in the years 1990 - 2023. 





