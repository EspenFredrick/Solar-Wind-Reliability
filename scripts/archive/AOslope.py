import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress
import os

def closestTo(inputList, val):
  arr = np.asarray(inputList)
  i = (np.abs(arr - val)).argmin()
  return arr[i]

def getSlopeInt(artemis, omni, workingDir):
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

            # Initialize empty storage arrays for slope and intercept of each timestep
            aoSlope = []
            aoInt = []

            # Initialize arrays which store the closest slope to 1, its index, and the y-intercept
            slopeClosestToOne = []
            intClosestToOne = []

            # Slide Artemis 30 times (for a 30-minute shift) over the Omni set and append the metric to each array
            for i in range(31):
                slope, intercept, rvalue, pvalue, stderr = linregress(artemis[k][aStart-i:aStop-i], omni[k][n:n+59])
                aoSlope.append(slope)
                aoInt.append(intercept)

            slopeClosestToOne.extend([closestTo(aoSlope, 1), aoSlope.index(closestTo(aoSlope, 1))])
            dataRows.append(np.concatenate(([omni['Time'][n]], [omni['Time'][n+59]], slopeClosestToOne[0]), axis=None))

            plt.scatter(artemis[k][aStart-aoSlope.index(closestTo(aoSlope, 1)):aStop-aoSlope.index(closestTo(aoSlope, 1))], omni[k][n:n+59], color="red", marker="o", label="Original data")
            y_pred = aoInt[aoSlope.index(closestTo(aoSlope, 1))] + closestTo(aoSlope, 1) * artemis[k][aStart-aoSlope.index(closestTo(aoSlope, 1)):aStop-aoSlope.index(closestTo(aoSlope, 1))]
            plt.plot(artemis[k][aStart-aoSlope.index(closestTo(aoSlope, 1)):aStop-aoSlope.index(closestTo(aoSlope, 1))], y_pred, color="green", label="Fitted line")

            if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/slopes/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k))):
                plt.savefig(os.path.join(workingDir,'Solar-Wind-Reliability/output-data/slopes/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))),dpi=300)
            else:
                os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/slopes/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
                plt.savefig(os.path.join(workingDir,'Solar-Wind-Reliability/output-data/slopes/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))),dpi=300)
            plt.close()
        eventMetadata = pd.DataFrame(dataRows, columns=['Start', 'Stop', 'Slope'])

        if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/slopes/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k))):
            eventMetadata.to_csv(os.path.join(workingDir,'Solar-Wind-Reliability/output-data/slopes/{}/{}/output.csv'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
        else:
            os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/slopes/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
            eventMetadata.to_csv(os.path.join(workingDir,'Solar-Wind-Reliability/output-data/slopes/{}/{}/output.csv'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))

    print('Done.')

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
        if not omniFileList[l].startswith('.') and not 'copy' in omniFileList[l]:
            print('Correlating {}...'.format(omniFileList[l]))
            artemisData = pd.read_csv(os.path.join(artemisDirectory, artemisFileList[l]), delimiter=',', header=0)
            omniData = pd.read_csv(os.path.join(omniDirectory, omniFileList[l]), delimiter=',', header=0)
            artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
            omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')

            getSlopeInt(artemisData, omniData, projDir)

elif int(toCorrelate) < len(omniFileList):
    print('Correlating {} and {}...'.format(omniFileList[int(toCorrelate)], artemisFileList[int(toCorrelate)]))
    artemisData = pd.read_csv(os.path.join(artemisDirectory, artemisFileList[int(toCorrelate)]), delimiter=',', header=0)
    omniData = pd.read_csv(os.path.join(omniDirectory, omniFileList[int(toCorrelate)]), delimiter=',', header=0)
    artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
    omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')

    getSlopeInt(artemisData, omniData, projDir)

else:
    raise ValueError('Must be "any" or less than {}'.format(len(omniFileList)))