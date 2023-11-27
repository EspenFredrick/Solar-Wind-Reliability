'''
This script takes the time shift for every hour interval by correlation coefficient and by slope, and plots ARTEMIS and OMNI on top of each other.
It also generates the scatter plot of ARTEMIS as a function of OMNI shifted by the slope closest to 1 and fits a curve through it, giving the slope and the intercept
'''

#Import statements:
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator
import os
import multiprocessing
import time

def makeScatter(x, y1, y2, UB, LB, slope, intercept, date, tStart, tStop, metric, unit):
    fig = plt.figure(figsize=(6, 10), constrained_layout=True)

    gridspec = fig.add_gridspec(nrows=9, ncols=5)
    axes = {}
    axes['shiftByCorr'] = fig.add_subplot(gridspec[0:2, 0:5])
    axes['shiftBySlope'] = fig.add_subplot(gridspec[2:4, 0:5])
    axes['scatterPlot'] = fig.add_subplot(gridspec[4:9, 0:5])

    bfX = np.arange(-51, 51, 1)
    bfY = intercept + (slope * bfX)

    axes['shiftByCorr'].plot([j for j in range(0, 60)], x, label='OMNI')
    axes['shiftByCorr'].plot([j for j in range(0, 60)], y1, label='ARTEMIS')
    axes['shiftByCorr'].set(xlim=(0, 59), ylim=(LB, UB), xlabel=('Minute of hour'), ylabel=('{}'.format(unit)))
    axes['shiftByCorr'].xaxis.set_minor_locator(MultipleLocator(1))
    axes['shiftByCorr'].xaxis.set_major_locator(MultipleLocator(5))
    axes['shiftByCorr'].legend()

    axes['shiftBySlope'].plot([j for j in range(0, 60)], x, label='OMNI')
    axes['shiftBySlope'].plot([j for j in range(0, 60)], y2, label='ARTEMIS')
    axes['shiftBySlope'].set(xlim=(0, 59), ylim=(LB, UB), xlabel=('Minute of hour'), ylabel=('{}'.format(unit)))
    axes['shiftBySlope'].xaxis.set_minor_locator(MultipleLocator(1))
    axes['shiftBySlope'].xaxis.set_major_locator(MultipleLocator(5))
    axes['shiftBySlope'].legend()

    axes['scatterPlot'].scatter(x, y2, s=8)
    axes['scatterPlot'].plot(bfX, bfY, color='red', linestyle='dashed')
    axes['scatterPlot'].axhline(color='black', linewidth=axes['scatterPlot'].spines['top'].get_linewidth())
    axes['scatterPlot'].axvline(color='black', linewidth=axes['scatterPlot'].spines['top'].get_linewidth())
    axes['scatterPlot'].xaxis.set_major_locator(MultipleLocator(10))
    axes['scatterPlot'].yaxis.set_major_locator(MultipleLocator(10))
    axes['scatterPlot'].set(xlim=(-31, 31), ylim=(-31, 31), xlabel='OMNI {}'.format(unit), ylabel='ARTEMIS {}'.format(unit), aspect='equal')

def doPlotRoutine(omniFile, artemisFile, metricFolder):
    #Load in OMNI and ARTEMIS files
    artemisData = pd.read_csv(artemisFile, delimiter=',', header=0, index_col=0)
    omniData = pd.read_csv(omniFile, delimiter=',', header=0, index_col=0)

    artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
    omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')

    # Plot the data for each
    keys = ['BY_GSE', 'BZ_GSE']
    units = [r'$B_y$ (nT)', r'$B_z$ (nT)']

    numWindows = len(omniData) - 60  # Number of 1-hour blocks in the data set
    for n in range(numWindows):
        aStart = (artemisData.loc[artemisData['Time'] == omniData['Time'][n]]).index[0]
        aStop = (artemisData.loc[artemisData['Time'] == omniData['Time'][n + 60]]).index[0]


        for k, u in zip(keys, units):
            shiftVals = pd.read_csv(os.path.join(metricFolder, k, 'timeshifts.csv'), delimiter=',', header=0, index_col=0)
            slopeVals = pd.read_csv(os.path.join(metricFolder, k, 'metrics.csv'), delimiter=',', header=0, index_col=0)

            pearson_shift = shiftVals['Pearson'][n]
            slope_shift = shiftVals['Slope'][n]
            slopes = slopeVals['Slope'][n]
            intercepts = slopeVals['Intercept'][n]

            upperBound = max([max(omniData[k]), max(artemisData[k])]) + 5
            lowerBound = min([min(omniData[k]), min(artemisData[k])]) - 5

            omni_slice = omniData[k][n:n+60]
            artemis_slice_pearson = artemisData[k][aStart-pearson_shift:aStop-pearson_shift]
            artemis_slice_slope = artemisData[k][aStart-slope_shift:aStop-slope_shift],

            makeScatter(omni_slice, artemis_slice_pearson, artemis_slice_slope, upperBound, lowerBound, slopes, intercepts, omniData['Time'][n].strftime('%Y-%m-%d'), omniData['Time'][n].strftime('%H:%M'), omniData['Time'][n+59].strftime('%H:%M'), k, u, pearson_shift, slope_shift)

            if os.path.exists(os.path.join('/Volumes/Research/Solar-Wind-Reliability/output-data/scatterplots-multicore/{}/{}/'.format(omniData['Time'][n].strftime('%Y-%m-%d'), k))):
                plt.savefig(os.path.join('/Volumes/Research/Solar-Wind-Reliability/output-data/scatterplots-multicore/{}/{}/{}.png'.format(omniData['Time'][n].strftime('%Y-%m-%d'), k, omniData['Time'][n].strftime('%H-%M'))), dpi=300)
            else:
                os.makedirs(os.path.join('/Volumes/Research/Solar-Wind-Reliability/output-data/scatterplots-multicore/{}/{}/'.format(omniData['Time'][n].strftime('%Y-%m-%d'), k)))
                plt.savefig(os.path.join('/Volumes/Research/Solar-Wind-Reliability/output-data/scatterplots-multicore/{}/{}/{}.png'.format(omniData['Time'][n].strftime('%Y-%m-%d'), k, omniData['Time'][n].strftime('%H-%M'))), dpi=300)
            plt.close()




# ARTEMIS, OMNI, and metric data directories. Please change these to the correct directories for your instance of this project.
artemisDataDirectory = '/Volumes/Research/Solar-Wind-Reliability/output-data/GSE/Artemis/'
omniDataDirectory = '/Volumes/Research/Solar-Wind-Reliability/output-data/GSE/Omni/'
metricDirectory = '/Volumes/Research/Solar-Wind-Reliability/output-data/hourly-correlations/'

omniFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(omniDataDirectory, x)), os.listdir(omniDataDirectory)))
artemisFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(artemisDataDirectory, x)), os.listdir(artemisDataDirectory)))
metricFolders = sorted(filter(lambda x: os.path.isdir(os.path.join(metricDirectory, x)), os.listdir(metricDirectory)))

omniFileList.remove('.DS_Store')
artemisFileList.remove('.DS_Store')
metricFolders.remove('merged')

def main():
    with multiprocessing.Pool() as pool:
        pool.starmap(doPlotRoutine, [(os.path.join(omniDataDirectory, oFile), os.path.join(artemisDataDirectory, aFile), os.path.join(metricDirectory, folder)) for oFile, aFile, folder in zip(omniFileList[0:2], artemisFileList[0:2], metricFolders[0:2])])

if __name__ == '__main__':
    start_time = time.time()

    multiprocessing.freeze_support()
    main()

    elapsed_time = time.time() - start_time
    print(f"Executed in {elapsed_time:.4f} seconds")