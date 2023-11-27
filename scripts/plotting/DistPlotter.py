import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import *
import numpy as np


def probDistGraph(series):
    fig, ax = plt.subplots(figsize=(8,4))
    binHeights = []
    for b in np.arange(1, -0.1, -0.1):
        counter = 0
        for s in series:
            if s >= b:
                counter = counter + 1
        binHeights.append(counter)
    print(binHeights)
    for h in range(len(binHeights)):
        binHeights[h] = 100*(binHeights[h]/len(series))
    plt.bar(['<1', '<0.9', '<0.8', '<0.7', '<0.6', '<0.5', '<0.4', '<0.3', '<0.2', '<0.1', '<0'], binHeights)
    plt.ylim(0,100)
    plt.ylabel('% Occurance')
    plt.xlabel('Bin')

#-----------------------------------------------------------------------------------------------------------------------
fDir = input('Enter the path to the project directory: ')

vars = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
for n, v in enumerate(vars):
    print('{} - {}'.format(n, v))
varToPlot = input('Please enter variable to plot or specify "all" to generate distribution plots for all variables: ')

corrs = ['Pearson', 'Slope', 'Intercept', 'MAPE', 'Ratio', 'RMSE', 'RMSE_Artemis', 'RMSE_Omni', 'RMSE_Avg', 'hourly-velocity']
for n, c in enumerate(corrs):
    print('{} - {}'.format(n, c))
corrToPlot = input('Please enter the metric to plot or specify "all" to generate distribution plots for for all metrics: ')
#-----------------------------------------------------------------------------------------------------------------------

if varToPlot == 'all':
    for v in vars:
        if corrToPlot == 'all':
            for c in corrs:
                path = os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged',v, 'output.csv')
                metricData = pd.read_csv(path, delimiter=',', header=0, index_col=0)
                probDistGraph(metricData[c])

                if os.path.exists(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/probability-dists', c)):
                    plt.savefig(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/probability-dists', c, '{}-{}.png'.format(v, c)), dpi=300)
                else:
                    os.makedirs(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/probability-dists', c))
                    plt.savefig(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/probability-dists', c, '{}-{}.png'.format(v, c)), dpi=300)

        elif int(corrToPlot) < len(corrs):
            path = os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToPlot)], 'output.csv')
            metricData = pd.read_csv(path, delimiter=',', header=0, index_col=0)
            probDistGraph(metricData[corrs[int(corrToPlot)]])

            if os.path.exists(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/probability-dists', corrs[int(corrToPlot)])):
                plt.savefig(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/probability-dists', corrs[int(corrToPlot)], '{}-{}.png'.format(vars[int(varToPlot)], corrs[int(corrToPlot)])), dpi=300)
            else:
                os.makedirs(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/probability-dists', corrs[int(corrToPlot)]))
                plt.savefig(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/probability-dists', corrs[int(corrToPlot)], '{}-{}.png'.format(vars[int(varToPlot)], corrs[int(corrToPlot)])), dpi=300)

elif int(varToPlot) < len(vars):
    if corrToPlot == 'all':
        print('placeholder')
    elif int(corrToPlot) < len(corrs):
        path = os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToPlot)], 'output.csv')
        metricData = pd.read_csv(path, delimiter=',', header=0, index_col=0)
        probDistGraph(metricData[corrs[int(corrToPlot)]])

        if os.path.exists(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists')):
            plt.savefig(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists', '{}-{}.png'.format(vars[int(varToPlot)], corrs[int(corrToPlot)])), dpi=300)
        else:
            os.makedirs(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists'))
            plt.savefig(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists', '{}-{}.png'.format(vars[int(varToPlot)], corrs[int(corrToPlot)])), dpi=300)


else:
    raise ValueError('Variable not in range or not "all".')