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
            if s > b:
                counter = counter + 1
        binHeights.append(counter)
    print(binHeights)
    for h in range(len(binHeights)):
        binHeights[h] = 100*(binHeights[h]/len(series))
    plt.bar(['>1', '>0.9', '>0.8', '>0.7', '>0.6', '>0.5', '>0.4', '>0.3', '>0.2', '>0.1', '>0'], binHeights)


def histTest(series):
    fig, ax = plt.subplots(figsize=(8,4))
    plt.hist(series, np.arange(0, 1.1, 0.1), cumulative=True, align='right')

#-----------------------------------------------------------------------------------------------------------------------
fDir = input('Enter the path to the project directory: ')

vars = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
for n, v in enumerate(vars):
    print('{} - {}'.format(n, v))
varToPlot = input('Please enter variable to plot or specify "all" to generate distribution plots for all variables: ')

corrs = ['R', 'Rho', 'Tau', 'MAPE', 'RMSE', 'Ratio']
for n, c in enumerate(corrs):
    print('{} - {}'.format(n, c))
corrToPlot = input('Please enter the metric to plot or specify "all" to generate distribution plots for for all metrics: ')
#-----------------------------------------------------------------------------------------------------------------------

if varToPlot == 'all':
    print('placeholder')
elif int(varToPlot) < len(vars):
    if corrToPlot == 'all':
        print('placeholder')
    elif int(corrToPlot) < len(corrs):
        path = os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToPlot)], 'output.csv')
        metricData = pd.read_csv(path, delimiter=',', header=0, index_col=0)
        histTest(metricData[corrs[int(corrToPlot)]])

        if os.path.exists(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists')):
            plt.savefig(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists', '{}.png'.format(vars[int(varToPlot)])), dpi=300)
        else:
            os.makedirs(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists'))
            plt.savefig(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists', '{}.png'.format(vars[int(varToPlot)])), dpi=300)

        probDistGraph(metricData[corrs[int(corrToPlot)]])
        if os.path.exists(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists')):
            plt.savefig(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists', '{}-bar.png'.format(vars[int(varToPlot)])), dpi=300)
        else:
            os.makedirs(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists'))
            plt.savefig(os.path.join(fDir,'Solar-Wind-Reliability/output-data/probability-dists', '{}-bar.png'.format(vars[int(varToPlot)])), dpi=300)



else:
    raise ValueError('Variable not in range or not "all".')