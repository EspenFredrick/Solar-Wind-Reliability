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

fDir = '/Volumes/Research'
folders = [f for f in os.listdir(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations'))]

vars = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
for n, v in enumerate(vars):
    print('{} - {}'.format(n, v))
varToMerge = input('Please enter variable to merge or specify "all" to generate merged files for all variables: ')
#if os.path.isfile(os.path.join("../output-data/hourly-correlations/", f)) and f.endswith(".csv")

if varToMerge == 'all':
    dirWithDates = os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/')
    folderList = sorted(filter(lambda x: os.path.isdir(os.path.join(dirWithDates, x)), os.listdir(dirWithDates)))

    for v in vars:
        for nums, folderNames in enumerate(folderList):
            frame = []
            if not folderNames.startswith('.') and folderNames != 'merged':
                file = pd.read_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations', folderNames, v, 'metrics.csv'), delimiter=',', header=0, index_col=0)
                frame.append(file)

        df = pd.concat(frame)
        df = df.reset_index(drop=True)

        if os.path.exists(
                os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', v)):
            df.to_csv(
                os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', v, 'output.csv'))
        else:
            os.makedirs(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', v))
            df.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', v,'output.csv'))

elif int(varToMerge) < len(vars):
    dirWithDates = os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/')
    folderList = sorted(filter(lambda x: os.path.isdir(os.path.join(dirWithDates, x)), os.listdir(dirWithDates)))

    for nums, folderNames in enumerate(folderList):
        frame = []
        if not folderNames.startswith('.') and folderNames != 'merged':
            file = pd.read_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations', folderNames, vars[int(varToMerge)], 'metrics.csv'), delimiter=',', header=0, index_col=0)
            frame.append(file)

    df = pd.concat(frame)
    df = df.reset_index(drop=True)

    if os.path.exists(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)])):
        df.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)], 'output.csv'))
    else:
        os.makedirs(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)]))
        df.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)], 'output.csv'))
else:
    raise ValueError('Variable not in range or not "all".')