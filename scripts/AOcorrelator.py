import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
import os

# Correlation metrics: Mean Abs Percent Err, Root Mean Sq Err, Ratio of timeseries
def corrMetrics(omni, artemis):
    mape = (1/60) * (np.sum([abs(((a - o)/a)) for o, a in zip(omni, artemis)]))
    rmse = np.sqrt(np.sum([((a - o)**2)/60 for o, a in zip(omni, artemis)]))
    ratio = np.average([abs(o/a) for o, a in zip(omni, artemis)])
    return mape, rmse, ratio

# Function to compute the correlation metrics.
def correlate(artemis, omni, workingDir):
    # Variables to loop over and their respective units
    keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
    dataRows = []
    numWindows = len(omni)-59 # Number of 1-hour blocks in the data set

    for k in keys:
        print('Key {}: Computing {} windows...'.format(k, numWindows))

        for n in range(numWindows): # Loop over each block
        # Find the start and stop index in Artemis that matches the nth and n+59th window of Omni
            aStart = (artemis.loc[artemis['Time'] == omni['Time'][n]]).index[0]
            aStop = (artemis.loc[artemis['Time'] == omni['Time'][n+59]]).index[0]

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

                mape, rmse, ratio = corrMetrics(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])
                mStore.append(mape)
                rmseStore.append(rmse)
                ratioStore.append(ratio)

            # Keep the largest positive value if some are positive, otherwise take most negative value
            # Store the maximum metric value in position 0, and the index at which it occurs (time shift) in position 1
            for corrs, maxes in zip([rStore, rhoStore, tauStore], [rMax, rhoMax, tauMax]):
                if all(c < 0 for c in corrs[1:]):
                    maxes.extend([max(corrs[1:], key=abs), corrs.index(max(corrs[1:], key=abs))])
                else:
                    maxes.extend([max(corrs[1:]), corrs.index(max(corrs[1:]))])

            for corrs, mins in zip([mStore, rmseStore, ratioStore], [mMin, rmseMin, ratioMin]):
                mins.extend([min(corrs[1:]), corrs.index(min(corrs[1:]))])

            dataRows.append(np.concatenate(([omni['Time'][n]], [omni['Time'][n+59]], rMax[0], rhoMax[0], tauMax[0], mMin[0], rmseMin[0], ratioMin[0]), axis=None))

        eventMetadata = pd.DataFrame(dataRows, columns=['Start', 'Stop','R', 'Rho', 'Tau', 'MAPE', 'RMSE', 'Ratio'])

        if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k))):
            eventMetadata.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/output.csv'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
        else:
            os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
            eventMetadata.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/output.csv'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))

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
