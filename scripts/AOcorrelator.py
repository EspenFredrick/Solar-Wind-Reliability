import numpy as np
import pandas as pd
from scipy.stats import pearsonr, linregress
import os

# Find slope closest to _...
def closestTo(inputList, val):
  arr = np.asarray(inputList)
  i = (np.abs(arr - val)).argmin()
  return arr[i]

# Correlation metrics
def corrMetrics(omni, artemis):
    mape = (1/60) * (np.sum([abs(((a - o)/a)) for o, a in zip(omni, artemis)]))
    ratio = np.average([(abs(o - a) / abs(a)) for o, a in zip(omni, artemis)])
    rmse = np.sqrt(np.sum([((a - o) ** 2) / 60 for o, a in zip(omni, artemis)]))
    rmseArtemis = np.sqrt(np.sum([((a - o) ** 2) / (a ** 2) if a != 0 else 0 for o, a in zip(omni, artemis)]) / 60)
    rmseOmni = np.sqrt(np.sum([((a - o) ** 2) / (o ** 2) if o != 0 else 0 for o, a in zip(omni, artemis)]) / 60)
    rmseAverage = np.sqrt(np.sum([((a - o) ** 2) / (((a + o) / 2) ** 2) for o, a in zip(omni, artemis)]) / 60)

    slope, intercept, rvalue, pvalue, stderr = linregress(artemis, omni)

    return mape, ratio, rmse, rmseArtemis, rmseOmni, rmseAverage, slope, intercept

# Function to compute the correlation metrics.
def correlate(artemis, omni, workingDir):
    # Variables to loop over and their respective units
    keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
    numWindows = len(omni)-59 # Number of 1-hour blocks in the data set

    for k in keys:
        print('Key {}: Computing {} windows...'.format(k, numWindows))
        dataRows = []
        offsetRows = []

        for n in range(numWindows): # Loop over each block
        # Find the start and stop index in Artemis that matches the nth and n+59th window of Omni
            aStart = (artemis.loc[artemis['Time'] == omni['Time'][n]]).index[0]
            aStop = (artemis.loc[artemis['Time'] == omni['Time'][n+59]]).index[0]

            # Initialize empty storage arrays for each metric
            pearsonStore = []
            mapeStore = []
            ratioStore = []
            rmseStore = []
            artemisStore = []
            omniStore = []
            avgStore = []

            slopeStore = []
            intStore = []

            # Initialize arrays which store the maximum metric value and its index
            pearsonMax = []
            mapeMin = []
            ratioMin = []
            rmseMin = []
            artemisMin = []
            omniMin = []
            avgMin = []

            slopeClosestToOne = []

            # Slide Artemis 30 times (for a 30-minute shift) over the Omni set and append the metric to each array
            for i in range(31):
                corrcoef = pearsonr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0]
                mape, ratio, rmse, rmseArtemis, rmseOmni, rmseAverage, slopes, ints = corrMetrics(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])

                for vals, lists in zip([corrcoef, mape, ratio, rmse, rmseArtemis, rmseOmni, rmseAverage, slopes, ints], [pearsonStore, mapeStore, ratioStore, rmseStore, artemisStore, omniStore, avgStore, slopeStore, intStore]):
                    lists.append(vals)

            # Store the maximum Pearson correlation coef. in position 0, and the index at which it occurs (time shift) in position 1
            if all(c < 0 for c in pearsonStore[1:]):
                pearsonMax.extend([max(pearsonStore[1:], key=abs), pearsonStore.index(max(pearsonStore[1:], key=abs))])
            else:
                pearsonMax.extend([max(pearsonStore[1:]), pearsonStore.index(max(pearsonStore[1:]))])

            # Store the minimum values for the other correlations in position 0 and the index at which it occurs in position 1
            for corrs, mins in zip([mapeStore, ratioStore, rmseStore, artemisStore, omniStore, avgStore], [mapeMin, ratioMin, rmseMin, artemisMin, omniMin, avgMin]):
                mins.extend([min(corrs[1:]), corrs.index(min(corrs[1:]))])

            # Store the slope closest to 1
            slopeClosestToOne.extend([closestTo(slopeStore[1:], 1), slopeStore.index(closestTo(slopeStore[1:], 1)), intStore[slopeStore.index(closestTo(slopeStore[1:], 1))]])



            dataRows.append(np.concatenate(([omni['Time'][n]], [omni['Time'][n+59]], pearsonMax[0], slopeClosestToOne[0], slopeClosestToOne[2], mapeMin[0], ratioMin[0], rmseMin[0], artemisMin[0], omniMin[0], avgMin[0]), axis=None))
            offsetRows.append(np.concatenate(([omni['Time'][n]], [omni['Time'][n+59]], pearsonMax[1], slopeClosestToOne[1], mapeMin[1], ratioMin[1], rmseMin[1], artemisMin[1], omniMin[1], avgMin[1]), axis=None))

        eventMetadata = pd.DataFrame(dataRows, columns=['Start', 'Stop','Pearson', 'Slope', 'Intercept', 'MAPE', 'Ratio', 'RMSE', 'RMSE_Artemis', 'RMSE_Omni', 'RMSE_Avg'])
        eventTimeShifts = pd.DataFrame(offsetRows, columns=['Start', 'Stop','Pearson', 'Slope', 'MAPE', 'Ratio', 'RMSE', 'RMSE_Artemis', 'RMSE_Omni', 'RMSE_Avg'])

        if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d_%H-%M'), k))):
            eventMetadata.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/metrics.csv'.format(omni['Time'][n].strftime('%Y-%m-%d_%H-%M'), k)))
            eventTimeShifts.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/timeshifts.csv'.format(omni['Time'][n].strftime('%Y-%m-%d_%H-%M'), k)))

        else:
            os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d_%H-%M'), k)))
            eventMetadata.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/metrics.csv'.format(omni['Time'][n].strftime('%Y-%m-%d_%H-%M'), k)))
            eventTimeShifts.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/timeshifts.csv'.format(omni['Time'][n].strftime('%Y-%m-%d_%H-%M'), k)))

    print('Done.')

#-----------------------------------------------------------------------------------------------------------------------

#projDir = input('Enter the path to the project directory: ')
projDir ='/Volumes/Research'
artemisDirectory = os.path.join(projDir, 'Solar-Wind-Reliability/output-data/GSE/Artemis/')
omniDirectory = os.path.join(projDir, 'Solar-Wind-Reliability/output-data/GSE/Omni/')

omniFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(omniDirectory, x)), os.listdir(omniDirectory)))
artemisFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(artemisDirectory, x)), os.listdir(artemisDirectory)))
for nums, files in enumerate(omniFileList):
    print('{} - {}'.format(nums, files))
toCorrelate = input('Please enter the number of the file you wish to correlate, or type "all" to correlate the whole folder: ')

if toCorrelate == 'all':
    for l in range(len(omniFileList)):
        if not omniFileList[l].startswith('.') and not 'copy' in omniFileList[l]:
            print('Correlating {}...'.format(omniFileList[l]))
            artemisData = pd.read_csv(os.path.join(artemisDirectory, artemisFileList[l]), delimiter=',', header=0)
            omniData = pd.read_csv(os.path.join(omniDirectory, omniFileList[l]), delimiter=',', header=0)
            artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
            omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')

            correlate(artemisData, omniData, projDir)

elif int(toCorrelate) < len(omniFileList):
    print('Correlating {} and {}...'.format(omniFileList[int(toCorrelate)], artemisFileList[int(toCorrelate)]))
    artemisData = pd.read_csv(os.path.join(artemisDirectory, artemisFileList[int(toCorrelate)]), delimiter=',', header=0)
    omniData = pd.read_csv(os.path.join(omniDirectory, omniFileList[int(toCorrelate)]), delimiter=',', header=0)
    artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
    omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')

    correlate(artemisData, omniData, projDir)

else:
    raise ValueError('Must be "any" or less than {}'.format(len(omniFileList)))
