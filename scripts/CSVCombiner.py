#----------------------------------------------------------------------------------------------------------------------------
#
#
#       $$$$$$   /$$$$$$  /$$    /$$  /$$$$$$                          /$$       /$$
#     /$$__  $$ /$$__  $$| $$   | $$ /$$__  $$                        | $$      |__/
#    | $$  \__/| $$  \__/| $$   | $$| $$  \__/  /$$$$$$  /$$$$$$/$$$$ | $$$$$$$  /$$ /$$$$$$$   /$$$$$$   /$$$$$$
#    | $$      |  $$$$$$ |  $$ / $$/| $$       /$$__  $$| $$_  $$_  $$| $$__  $$| $$| $$__  $$ /$$__  $$ /$$__  $$
#    | $$       \____  $$ \  $$ $$/ | $$      | $$  \ $$| $$ \ $$ \ $$| $$  \ $$| $$| $$  \ $$| $$$$$$$$| $$  \__/
#    | $$    $$ /$$  \ $$  \  $$$/  | $$    $$| $$  | $$| $$ | $$ | $$| $$  | $$| $$| $$  | $$| $$_____/| $$
#    |  $$$$$$/|  $$$$$$/   \  $/   |  $$$$$$/|  $$$$$$/| $$ | $$ | $$| $$$$$$$/| $$| $$  | $$|  $$$$$$$| $$
#     \______/  \______/     \_/     \______/  \______/ |__/ |__/ |__/|_______/ |__/|__/  |__/ \_______/|__/
#
#                                            -- By Espen Fredrick --
#                                                   04/25/2023
#
# Simple script to import all the data files in a given folder and merge them together.
#----------------------------------------------------------------------------------------------------------------------------

import pandas as pd
import os

fDir = input('Enter the path to the project directory: ')
folders = [f for f in os.listdir(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations'))]

vars = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
for n, v in enumerate(vars):
    print('{} - {}'.format(n, v))
varToMerge = input('Please enter variable to merge or specify "all" to generate merged files for all variables: ')
#if os.path.isfile(os.path.join("../output-data/hourly-correlations/", f)) and f.endswith(".csv")

if varToMerge == 'all':
    print('placeholder')
    #stuff
elif int(varToMerge) < len(vars):
    frame = []
    for folderName in folders:
        if not folderName.startswith('.') and folderName != 'merged':

            file = pd.read_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations', folderName, vars[int(varToMerge)], 'output.csv'), delimiter=',', header=0, index_col=0)
            frame.append(file)
    df = pd.concat(frame)
    if os.path.exists(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)])):
        df.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)], 'output.csv'))
    else:
        os.makedirs(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)]))
        df.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)], 'output.csv'))
else:
    raise ValueError('Variable not in range or not "all".')