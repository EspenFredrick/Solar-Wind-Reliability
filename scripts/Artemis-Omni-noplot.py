import numpy as np
import pandas as pd
import os
def correlate(sliding, fixed, sat1Name, sat2Name):
    dataRows = []
    offsetRows = []
    numWindows = len(fixed['Time']) - 59

    for j in range(numWindows): # Find the correlation coefficient over 'numWindows' hour-intervals
        sliding_start = (sliding.loc[sliding['Time'] == fixed['Time'][j]]).index[0] # Set the start time of the sliding index where the timestamp of the fixed series begins
        sliding_stop = (sliding.loc[sliding['Time'] == fixed['Time'][j+59]]).index[0] # Set the end of the sliding index an hour after the start of the fixed series

        keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
        pMaxes = []
        ratioMaxes =[]
        pOffsets = []
        ratioOffsets = []

        for k in keys:
            corrStore = [] # Temp storage array for coefficients
            ratioStore = []

            for n in range(31): # Calculate a coefficient over a 0 to 30-min window
                corrStore.append(np.corrcoef(fixed[k][j:j+59], sliding[k][sliding_start-n:sliding_stop-n])[0, 1])  # Append the storage arrays
                #ratioStore.append(np.nanmean([((j*i)/(np.abs(j*i)))*(1/(1+np.abs(j-i))) for i, j in zip(sliding[k][sliding_start - n:sliding_stop - n].to_numpy(), fixed[k][j:j + 60].to_numpy())]))
                ratioStore.append(np.nanmean([((o-a)/a) for a, o in zip(sliding[k][sliding_start - n:sliding_stop - n].to_numpy(), fixed[k][j:j + 60].to_numpy())]))
                

            if all(corrs < 0 for corrs in corrStore[1:]):
                pMaxes.append(max(corrStore[1:], key=abs))
                pOffsets.append(corrStore.index(max(corrStore[1:], key=abs)))

            else:
                pMaxes.append(max(corrStore[1:]))
                pOffsets.append(corrStore.index(max(corrStore[1:])))

            ratioMaxes.append(max(ratioStore[1:]))
            ratioOffsets.append(ratioStore.index(max(ratioStore[1:])))


            dataRows.append(np.concatenate(([fixed['Time'][j]], [fixed['Time'][j+59]], pMaxes, ratioMaxes), axis=None))
            offsetRows.append(np.concatenate(([fixed['Time'][j]], [fixed['Time'][j+59]], pOffsets, ratioOffsets), axis=None))

    return dataRows #Output the entire chunk of metadata

timeList = ['2011-10-24_18-10', '2011-12-28_16-20', '2013-01-17_10-30', '2014-02-27_16-30', '2014-02-27_18-30', '2014-04-05_19-30', '2015-03-16_03-50', '2015-03-17_04-20', '2015-04-20_20-10', '2015-06-12_17-10', '2016-06-05_05-00', '2016-08-02_12-15', '2017-09-15_12-00', '2017-09-27_04-30', '2018-09-13_00-00', '2018-10-09_04-00', '2019-11-27_13-00', '2021-01-11_10-00']
#timeList = ['2011-12-28_16-20']

#eventSelector = input('Enter the file date to correlate (in yyyy-mm-dd_hh-mm format): ')
sat1Directory = '../output-data/Artemis/'
sat1Name = 'Artemis'
sat2Directory = '../output-data/Omni/'
sat2Name = 'Omni'

for eventSelector in timeList:
    sat1Data = pd.read_csv(os.path.join(sat1Directory, '{}_{}.csv'.format(sat1Name, eventSelector)), delimiter=',', header=0)
    sat1Data['Time'] = pd.to_datetime(sat1Data['Time'], format='%Y-%m-%d %H:%M:%S')
    sat2Data = pd.read_csv(os.path.join(sat2Directory, '{}_{}.csv'.format(sat2Name, eventSelector)), delimiter=',', header=0)
    sat2Data['Time'] = pd.to_datetime(sat2Data['Time'], format='%Y-%m-%d %H:%M:%S')

    eventMetadata = pd.DataFrame(correlate(sat1Data, sat2Data, sat1Name, sat2Name), columns=['Start', 'Stop', 'P(Bx)', 'P(By)', 'P(Bz)', 'P(Vx)', 'P(Vy)', 'P(Vz)', 'P(n)', 'P(T)', 'R(Bx)', 'R(By)', 'R(Bz)', 'R(Vx)', 'R(Vy)', 'R(Vz)', 'R(n)', 'R(T)'])
    eventMetadata.to_csv('../output-data/hourly-correlations/{}_{}_{}.csv'.format(sat1Name, sat2Name, eventSelector))
#%%
