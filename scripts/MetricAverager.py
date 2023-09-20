import numpy as np
import pandas as pd
import os

fDir = input('Enter the path to the project directory: ')
folders = [f for f in os.listdir(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations'))]

vars = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
for n, v in enumerate(vars):
    print('{} - {}'.format(n, v))
varToAvg = input('Please enter variable to merge or specify "all" to generate merged files for all variables: ')

#if os.path.isfile(os.path.join("../output-data/hourly-correlations/", f)) and f.endswith(".csv")

if varToAvg == 'all':
    print('placeholder')
    #stuff

elif int(varToAvg) < len(vars):
    for folderName in folders:
        if not folderName.startswith('.') and folderName != 'merged':
            file = pd.read_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations', folderName, vars[int(varToAvg)], 'output.csv'), delimiter=',', header=0, index_col=0)

            avgs = []
            for cNames in file.columns[2:]:
                avgs.append(np.average(file[cNames]))
            computed = pd.DataFrame(avgs, index=file.columns[2:])
            computed.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations', folderName, vars[int(varToAvg)], 'averaged.csv'))
else:
    raise ValueError('Variable not in range or not "all".')


'''
    if os.path.exists(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)])):
        df.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)], 'output.csv'))
    else:
        os.makedirs(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)]))
        df.to_csv(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToMerge)], 'output.csv'))
'''