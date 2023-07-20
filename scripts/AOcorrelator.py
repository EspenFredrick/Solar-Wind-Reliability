import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
import os

# Mean Absolute Percent Error (MAPE) function
def meanAbsPercErr(artemis, omni, key):
    if any([((a - o)/a) for o, a in zip(omni, artemis)]) == np.nan:
        print('NaN encountered in key {}'.format(key))
    else:
        print('No NaN found in {}'.format(key))
    #m = (1/60) * (np.nanmean([((a - o)/a) for o, a in zip(omni, artemis)]))
    m=0.5
    return m

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
def lineplot(ax, x, artemisLine, omniLine, unit):
    ax.set_ylim(1.5*min(omniLine), 1.5*abs(max(omniLine)))
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
        aStop = (artemis.loc[artemis['Time'] == omni['Time'][n + 59]]).index[0]
        # Variables to loop over and their respective units
        keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
        units = [r'$B_x$ (nT)', r'$B_y$ (nT)', r'$B_z$ (nT)', r'$V_x$ (km/s)', r'$V_y$ (km/s)', r'$V_z$ (km/s)', r'Density ($cm^{-3}$)', 'Temperature (K)']

        for k, u in zip(keys, units):
            # Initialize empty storage arrays for each metric
            rStore = []
            rhoStore = []
            tauStore = []
            mStore = []
            # Initialize arrays which store the maximum metric value and its index
            rMax = []
            rhoMax = []
            tauMax = []
            mMax = []

            # Slide Artemis 30 times (for a 30-minute shift) over the Omni set and append the metric to each array
            for i in range(31):
                rStore.append(pearsonr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0])
                rhoStore.append(spearmanr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0])
                tauStore.append(kendalltau(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0])
                mStore.append(meanAbsPercErr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i], k))

            # Keep the largest positive value if some are positive, otherwise take most negative value
            # Store the maximum metric value in position 0, and the index at which it occurs (time shift) in position 1
            for corrs, maxes in zip([rStore, rhoStore, tauStore, mStore], [rMax, rhoMax, tauMax, mMax]):
                if all(c < 0 for c in corrs[1:]):
                    maxes.extend([max(corrs[1:], key=abs), corrs.index(max(corrs[1:], key=abs))])
                else:
                    maxes.extend([max(corrs[1:]), corrs.index(max(corrs[1:]))])

            # Initialize the scatter plots and line plots. Top row are scatter plots, bottom row are line plots
            fig, ((p1, r1), (p2, r2), (t1, m1), (t2, m2)) = plt.subplots(nrows=4, ncols=2, figsize=(12,12))

            # Run the scatter plot and line plot functions to plot how the metric changes, and the overlapping series
            # Create a vertical line to the maximum metric value and highlight it red
            for axs, vars, maxes, labels in zip([p1, r1, t1, m1],[rStore, rhoStore, tauStore, mStore], [rMax, rhoMax, tauMax, mMax], ['Pearson R', 'Spearman Rho', 'Kendall Tau', 'MAPE']):
                scatterplot(axs, np.arange(0, 31, 1), vars)
                axs.scatter(maxes[1], maxes[0], color='red')
                axs.vlines(maxes[1], -1, maxes[0], color='red', linestyle='dashed')
                axs.set_title(labels)
            for axs2, maxes in zip([p2, r2, t2, m2], [rMax, rhoMax, tauMax, mMax]):
                lineplot(axs2, omni['Time'][n:n+59], omni[k][n:n+59], artemis[k][aStart-maxes[1]:aStop-maxes[1]], u)

            plt.suptitle('Comparison of Correlation Metrics')
            plt.tight_layout()
            if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k))):
                plt.savefig(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))), dpi=300)
            else:
                os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
                plt.savefig(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))), dpi=300)
            plt.close()
    print('Done.')