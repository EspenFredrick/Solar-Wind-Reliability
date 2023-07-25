import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
import os

# Mean Absolute Percent Error (MAPE) function
def meanAbsPercErr(omni, artemis):
    m = (1/60) * (np.sum([np.abs(((a - o)/a)) for o, a in zip(omni, artemis)]))
    return m
def rootMeanSqErr(omni, artemis):
    rmse = np.sqrt(np.sum([((a - o)**2)/60 for o, a in zip(omni, artemis)]))
    return rmse

def makeRatio(omni, artemis):
    ratio = np.average([abs(o/a) for o, a in zip(omni, artemis)])
    return ratio

# Function to create the scatter plots for each metric
def scatterplot(ax, x, y):
    ax.set_ylim(-1,1)
    ax.set_xlim(0, 30)
    ax.hlines(0, 0, 30, color='black', linestyle='dashed')
    ax.set_xlabel('Time Shift (min)')
    ax.set_ylabel('Correlation Value')
    ax.scatter(x, y)
    ax.xaxis.set_minor_locator(MultipleLocator(1))

# Function to create the line plots for each metric. This visualizes how they shift relative to another at peak correlation.
def lineplot(ax, x, omniLine, artemisLine, unit):
    ax.set_ylim(2*min(omniLine), 2*abs(max(omniLine)))
    ax.set_xlim(min(x), max(x))
    ax.set_xlabel('Time UTC')
    ax.set_ylabel(unit)
    ax.plot(x, omniLine, label='OMNI')
    ax.plot(x, artemisLine, label='Artemis')
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.legend(loc='lower right')

# Function to compute the correlation metrics.
def correlate(artemis, omni, workingDir='/Volumes/Research', r=True, rho=True, tau=True, makePlots = True):
    numWindows = len(omni)-59 # Number of 1-hour blocks in the data set

    for n in range(numWindows): # Loop over each block
        print('Computing window {} of {}...'.format(n+1, numWindows))

        # Find the start and stop index in Artemis that matches the nth and n+59th window of Omni
        aStart = (artemis.loc[artemis['Time'] == omni['Time'][n]]).index[0]
        aStop = (artemis.loc[artemis['Time'] == omni['Time'][n+59]]).index[0]
        # Debugging tool, uncomment to view start/stop values and indices
        #print('Artemis start: {}, Artemis stop: {}'.format(artemis['Time'][aStart], artemis['Time'][aStop]))
        #print('Index {} to {}'.format(aStart, aStop))
        #print('Omni start: {}, Omni stop: {}'.format(omni['Time'][n], omni['Time'][n+59]))
        #print('Index {} to {}'.format(n, n+59))

        # Variables to loop over and their respective units
        keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
        units = [r'$B_x$ (nT)', r'$B_y$ (nT)', r'$B_z$ (nT)', r'$V_x$ (km/s)', r'$V_y$ (km/s)', r'$V_z$ (km/s)', r'Density ($cm^{-3}$)', 'Temperature (K)']

        for k, u in zip(keys, units):
            # Initialize empty storage arrays for each metric
            rStore = []
            rhoStore = []
            tauStore = []
            mStore = []
            rmseStore = []
            ratioStore = []

            # Initialize arrays which store the maximum metric value and its index
            rMax = []
            rhoMax = []
            tauMax = []
            mMin = []
            rmseMin = []
            ratioMin = []

            # Slide Artemis 30 times (for a 30-minute shift) over the Omni set and append the metric to each array
            for i in range(31):
                rStore.append(pearsonr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0])
                rhoStore.append(spearmanr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0])
                tauStore.append(kendalltau(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0])
                mStore.append(meanAbsPercErr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i]))
                rmseStore.append(rootMeanSqErr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i]))
                ratioStore.append(makeRatio(omni[k][n:n+59], artemis[k][aStart-i:aStop-i]))

            # Keep the largest positive value if some are positive, otherwise take most negative value
            # Store the maximum metric value in position 0, and the index at which it occurs (time shift) in position 1
            for corrs, maxes in zip([rStore, rhoStore, tauStore], [rMax, rhoMax, tauMax]):
                if all(c < 0 for c in corrs[1:]):
                    maxes.extend([max(corrs[1:], key=abs), corrs.index(max(corrs[1:], key=abs))])
                else:
                    maxes.extend([max(corrs[1:]), corrs.index(max(corrs[1:]))])
            for corrs, mins in zip([mStore, rmseStore, ratioStore], [mMin, rmseMin, ratioMin]):
                mins.extend([min(corrs[1:]), corrs.index(min(corrs[1:]))])

            # Initialize the scatter plots and line plots. Top row are scatter plots, bottom row are line plots
            fig, ((p1, r1, t1), (p2, r2, t2), (m1, rmse1, ratio1), (m2, rmse2, ratio2)) = plt.subplots(nrows=4, ncols=3, figsize=(18,12))

            # Run the scatter plot and function to plot how the metric changes
            # Create a vertical line to the maximum metric value and highlight it red
            for axs, vars, maxes, labels in zip([p1, r1, t1],[rStore, rhoStore, tauStore], [rMax, rhoMax, tauMax], ['Pearson R', 'Spearman Rho', 'Kendall Tau']):
                scatterplot(axs, np.arange(0, 31, 1), vars)
                m1.set_ylim(0,2)
                axs.scatter(maxes[1], maxes[0], color='red')
                axs.vlines(maxes[1], -1, maxes[0], color='red', linestyle='dashed')
                axs.text(.01, .99,'Max = {}'.format(round(maxes[0], 3)), ha = 'left', va = 'top', transform = axs.transAxes)
                axs.set_title(labels)

            for axs, vars, mins, labels in zip([m1, rmse1, ratio1], [mStore, rmseStore, ratioStore], [mMin, rmseMin, ratioMin], ['MAPE', 'RMSE', 'Ratio']):
                axs.set_ylim(0, max(vars)+1)
                axs.set_xlim(0, 30)
                axs.set_xlabel('Time Shift (min)')
                axs.set_ylabel('Correlation Value')
                axs.scatter(np.arange(0, 31, 1), vars)
                axs.scatter(mins[1], mins[0], color='red')
                axs.vlines(mins[1], 0, mins[0], color='red', linestyle='dashed')
                axs.text(.01, .99, 'Max = {}'.format(round(mins[0], 3)), ha='left', va='top', transform=axs.transAxes)
                axs.xaxis.set_minor_locator(MultipleLocator(1))
                axs.set_title(labels)

            # Run the line plot function to plot how Artemis shifted by the time offset lines up
            for axs2, maxes in zip([p2, r2, t2, m2, rmse2, ratio2], [rMax, rhoMax, tauMax, mMin, rmseMin, ratioMin]):
                lineplot(axs2, omni['Time'][n:n+60], omni[k][n:n+60], artemis[k][aStart-maxes[1]:aStop-maxes[1]+1], u)
                axs2.set_title('Time Series Shift by Metric')
                axs2.text(.01, .99, 'Shift = {} min.'.format(round(maxes[1], 3)), ha='left', va='top', transform=axs2.transAxes)
            plt.suptitle('Comparison of Correlation Metrics', fontsize=18)
            plt.tight_layout()

            # Save images to directory
            if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k))):
                plt.savefig(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))), dpi=300)
            else:
                os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
                plt.savefig(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))), dpi=300)
            plt.close()
    print('Done.')

#-----------------------------------------------------------------------------------------------------------------------

projDir = input('Enter the path to the project directory: ')
artemisDirectory = os.path.join(projDir, 'Solar-Wind-Reliability/output-data/GSE/Artemis/')
omniDirectory = os.path.join(projDir, 'Solar-Wind-Reliability/output-data/GSE/Omni/')

omniFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(omniDirectory, x)), os.listdir(omniDirectory)))
artemisFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(artemisDirectory, x)), os.listdir(artemisDirectory)))
for nums, files in enumerate(omniFileList):
    print('{} - {}'.format(nums, files))
toCorrelate = input('Please enter the number of the file you wish to correlate, or type "all" to correlate the whole folder: ')

if toCorrelate == 'all':
    for l in range(len(omniFileList)):
        if not omniFileList[l].startswith('.'):
            print('Correlating {}...'.format(omniFileList[l]))
            artemisData = pd.read_csv(os.path.join(artemisDirectory, artemisFileList[l]), delimiter=',', header=0)
            omniData = pd.read_csv(os.path.join(omniDirectory, omniFileList[l]), delimiter=',', header=0)
            artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
            omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')

            correlate(artemisData, omniData, projDir)

elif int(toCorrelate) < len(omniFileList):
    print('Correlating {}...'.format(omniFileList[int(toCorrelate)]))
    artemisData = pd.read_csv(os.path.join(artemisDirectory, artemisFileList[int(toCorrelate)]), delimiter=',', header=0)
    omniData = pd.read_csv(os.path.join(omniDirectory, omniFileList[int(toCorrelate)]), delimiter=',', header=0)
    artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
    omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')

    correlate(artemisData, omniData, projDir)
else:
    raise ValueError('Must be "any" or less than {}'.format(len(omniFileList)))
