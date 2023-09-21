import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd
import os


fDir = '/Volumes/Research'


vars = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
for n, v in enumerate(vars):
    print('{} - {}'.format(n, v))
varToPlot = input('Please enter variable to plot or specify "all" to generate distribution plots for all variables: ')


if varToPlot == 'all':
    print('Keyword "all" is not yet supported. Please run again.')


elif int(varToPlot) < len(vars):
    dirWithFiles = os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToPlot)])
    fileList = sorted(filter(lambda x: os.path.isfile(os.path.join(dirWithFiles, x)), os.listdir(dirWithFiles)))
    for nums, files in enumerate(fileList):
        print('{} - {}'.format(nums, files))
    fileToPlot = input('Please enter the number of the file you wish to plot. ')

    path = os.path.join(fDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/merged', vars[int(varToPlot)], fileList[int(fileToPlot)])
    metricData = pd.read_csv(path, delimiter=',', header=0, index_col=0)
    params = {'pearson': metricData.iloc[:,2], 'slope': metricData.iloc[:,3], 'intercept': metricData.iloc[:,4]}

    keys = ['pearson', 'slope', 'intercept']
    for v,k in enumerate(keys):
        print('{} - {}'.format(v, k))
    varToHist = input('Please enter the number of the parameter you wish to plot. ')


    fig, ax = plt.subplots(figsize=(9,7))
    plt.hist(params[keys[int(varToHist)]], bins=np.arange(-1, 2.1, 0.1), edgecolor = "black")
    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    for rect in ax.patches:
        height = rect.get_height()
        ax.annotate(f'{int(height)}', xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5), textcoords='offset points', ha='center', va='bottom', fontsize=8)
    plt.title('Occurrence of best-fit intercept between ARTEMIS and Omni in IMF Bz')
    plt.xlabel('Bin')
    plt.ylabel('Frequency (counts)')

    plt.xlim(-1, 2)
    plt.savefig(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/', vars[int(varToPlot)]+'-slope.png'), dpi=300)
    plt.show()

else:
    raise ValueError('Variable not in range or not "all".')