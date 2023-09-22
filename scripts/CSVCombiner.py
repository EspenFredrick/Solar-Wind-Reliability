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

#fDir = input('Enter the path to the project directory: ')
fDir = '/Volumes/Research'
folders = [f for f in os.listdir(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations'))]

vars = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
for n, v in enumerate(vars):
    print('{} - {}'.format(n, v))
varToMerge = input('Please enter variable to merge or specify "all" to generate merged files for all variables: ')
#if os.path.isfile(os.path.join("../output-data/hourly-correlations/", f)) and f.endswith(".csv")

if varToMerge == 'all':
    print('placeholder')

elif int(varToMerge) < len(vars):
    dirWithFiles = os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/2011-10-24_22-30', vars[int(varToMerge)])
    fileList = sorted(filter(lambda x: os.path.isfile(os.path.join(dirWithFiles, x)), os.listdir(dirWithFiles)))
    for nums, files in enumerate(fileList):
        print('{} - {}'.format(nums, files))
    toCombine = input('Please enter the number of the file you wish to combine. ')

    frame = []
    for folderName in folders:
        if not folderName.startswith('.') and folderName != 'merged':
            print(folderName)
            file = pd.read_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations', folderName, vars[int(varToMerge)], fileList[int(toCombine)]), delimiter=',', header=0, index_col=0)
            frame.append(file)
    df = pd.concat(frame)
    df = df.reset_index(drop=True)

    if os.path.exists(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)])):
        df.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)], 'output'+fileList[int(toCombine)]))
    else:
        os.makedirs(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)]))
        df.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)], 'output'+fileList[int(toCombine)]))
else:
    raise ValueError('Variable not in range or not "all".')