import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd
import os


def surfacePlotter(corrs, slope):
    fig, ax = plt.subplots()
    plt.hist2d(corrs, slope, bins=[np.arange(-15,16,1), np.arange(-2,2.1,0.1)], range=[[-15, 15], [-2, 2]])
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    plt.title('Occurrence of Slope Relative to Delta-t')
    plt.xlabel('Delta-t between peak corr. coef. and slope closest to 1')
    plt.ylabel('Slope between Artemis/Omni')
    plt.colorbar()


#-----------------------------------------------------------------------------------------------------------------------
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
    surfacePlotter(metricData.iloc[:,6], metricData.iloc[:,3])
    plt.savefig(os.path.join(fDir, 'Solar-Wind-Reliability/output-data/', vars[int(varToPlot)]+'_zoomed_deltaT.png'), dpi=300)
    plt.show()

else:
    raise ValueError('Variable not in range or not "all".')

































'''
# make data with uneven sampling in x
x = [-3, -2, -1.6, -1.2, -.8, -.5, -.2, .1, .3, .5, .8, 1.1, 1.5, 1.9, 2.3, 3]
X, Y = np.meshgrid(x, np.linspace(-3, 3, 128))
Z = (1 - X/2 + X**5 + Y**3) * np.exp(-X**2 - Y**2)

# plot
fig, ax = plt.subplots()

ax.pcolormesh(X, Y, Z, vmin=-0.5, vmax=1.0)

plt.show()
'''