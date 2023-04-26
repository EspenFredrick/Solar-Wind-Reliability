import numpy as np
import pandas as pd
import os

def correlate(sliding, fixed, sat1Name, sat2Name):
    dataRows = []
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
            avgStore = []

            for n in range(31): # Calculate a coefficient over a 0 to 30-min window
                corrStore.append(np.corrcoef(fixed[k][j:j+59], sliding[k][sliding_start-n:sliding_stop-n])[0, 1])  # Append the storage arrays
                avgStore.append(np.average([min(i, j, key=abs) / max(i, j, key=abs) for i, j in zip(sliding[k][sliding_start - n:sliding_stop - n].to_numpy(), fixed[k][j:j + 60].to_numpy())]))

            if all(corrs < 0 for corrs in corrStore[1:]):
                pMaxes.append(max(corrStore[1:], key=abs))
                pOffsets.append(corrStore.index(max(corrStore[1:], key=abs)))

            else:
                pMaxes.append(max(corrStore[1:]))
                pOffsets.append(corrStore.index(max(corrStore[1:])))

            ratioMaxes.append(max(avgStore[1:]))
            ratioOffsets.append(avgStore.index(max(avgStore[1:])))

        dataRows.append(np.concatenate(([fixed['Time'][j]], [fixed['Time'][j+59]], pMaxes, pOffsets, ratioMaxes, ratioOffsets), axis=None))
    return dataRows #Output the entire chunk of metadata

eventSelector = input('Enter the file date to correlate (in yyyy-mm-dd_hh-mm format): ')
sat1Directory = '../metadata/Artemis/'
sat1Name = 'Artemis'
sat2Directory = '../metadata/Omni/'
sat2Name = 'Omni'

sat1Data = pd.read_csv(os.path.join(sat1Directory, '{}_{}.csv'.format(sat1Name, eventSelector)), delimiter=',', header=0)
sat1Data['Time'] = pd.to_datetime(sat1Data['Time'], format='%Y-%m-%d %H:%M:%S')
sat2Data = pd.read_csv(os.path.join(sat2Directory, '{}_{}.csv'.format(sat2Name, eventSelector)), delimiter=',', header=0)
sat2Data['Time'] = pd.to_datetime(sat2Data['Time'], format='%Y-%m-%d %H:%M:%S')

eventMetadata = pd.DataFrame(correlate(sat1Data, sat2Data, sat1Name, sat2Name), columns=['Start', 'Stop', 'P(Bx)', 'P(By)', 'P(Bz)', 'P(Vx)', 'P(Vy)', 'P(Vz)', 'P(n)', 'P(T)', 'pOffset (Bx)', 'pOffset (By)', 'pOffset (Bz)', 'pOffset (Vx)', 'pOffset (Vy)', 'pOffset (Vz)', 'pOffset (n)', 'pOffset (T)', 'R(Bx)', 'R(By)', 'R(Bz)', 'R(Vx)', 'R(Vy)', 'R(Vz)', 'R(n)', 'R(T)', 'rOffset (Bx)', 'rOffset (By)', 'rOffset (Bz)', 'rOffset (Vx)', 'rOffset (Vy)', 'rOffset (Vz)', 'rOffset (n)', 'rOffset (T)'])
eventMetadata.to_csv('../metadata/{}_{}_{}.csv'.format(sat1Name, sat2Name, eventSelector))