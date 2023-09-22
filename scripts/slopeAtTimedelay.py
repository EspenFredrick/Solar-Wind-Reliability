from scipy.stats import pearsonr, linregress
import numpy as np
import pandas as pd
import os

def closestTo(inputList, val):
  arr = np.asarray(inputList)
  i = (np.abs(arr - val)).argmin()
  return arr[i]

def correlate(artemis, omni, workingDir):
    # Variables to loop over and their respective units
    keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
    numWindows = len(omni)-59 # Number of 1-hour blocks in the data set

    for k in keys:
        print('Key {}: Computing {} windows...'.format(k, numWindows))
        dataRows = []

        for n in range(numWindows): # Loop over each block
            aStart = (artemis.loc[artemis['Time'] == omni['Time'][n]]).index[0]
            aStop = (artemis.loc[artemis['Time'] == omni['Time'][n+59]]).index[0]

            pearsonStore = []
            slopeStore = []

            pearsonMax = []
            slopeAtMaxP = []
            actualSlopeMax = []

            # Slide Artemis 30 times (for a 30-minute shift) over the Omni set and append the metric to each array
            for i in range(31):
                corrcoef = pearsonr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0]
                slope, intercept, rvalue, pvalue, stderr = linregress(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])

                for vals, lists in zip([corrcoef, slope], [pearsonStore, slopeStore]):
                    lists.append(vals)

            # Store the maximum Pearson correlation coef. in position 0, and the index at which it occurs (time shift) in position 1
            # Also store the slope at the time when the Pearson coef. is maximized
            if all(c < 0 for c in pearsonStore[1:]):
                pearsonMax.extend([max(pearsonStore[1:], key=abs), pearsonStore.index(max(pearsonStore[1:], key=abs))])
                slopeAtMaxP.extend([slopeStore[pearsonStore.index(max(pearsonStore[1:], key=abs))], slopeStore.index(slopeStore[pearsonStore.index(max(pearsonStore[1:], key=abs))])])
            else:
                pearsonMax.extend([max(pearsonStore[1:]), pearsonStore.index(max(pearsonStore[1:]))])
                slopeAtMaxP.extend([slopeStore[pearsonStore.index(max(pearsonStore[1:]))], slopeStore.index(slopeStore[pearsonStore.index(max(pearsonStore[1:]))])])

            actualSlopeMax.extend([closestTo(slopeStore, 1), slopeStore.index(closestTo(slopeStore, 1))])
            deltaT = pearsonMax[1] - actualSlopeMax[1]

            dataRows.append(np.concatenate(([omni['Time'][n]], [omni['Time'][n+59]], pearsonMax[0], slopeAtMaxP[0], pearsonMax[1], actualSlopeMax[1], deltaT), axis=None))

        eventMetadata = pd.DataFrame(dataRows, columns=['Start', 'Stop','Pearson', 'Slope', 'PearsonShift', 'SlopeShift', 'DeltaT'])

        if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k))):
            eventMetadata.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/slopes-at-timedelay.csv'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))

        else:
            os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
            eventMetadata.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/slopes-at-timedelay.csv'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))

    print('Done.')


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
