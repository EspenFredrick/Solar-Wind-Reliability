import numpy as np
import pandas as pd
import os

def correlate(sliding, fixed):

    rows = []
    for j in range(len(fixed['Time'])-61): # Take the number of data points and subtract an hour from it. That's how many times you can iterate a one-hour chunk
        sliding_start = (sliding.loc[sliding['Time'] == fixed['Time'][j]]).index[0] # Set the start time of the sliding index where the timestamp of the fixed series begins
        sliding_stop = (sliding.loc[sliding['Time'] == fixed['Time'][j+60]]).index[0] # Set the end of the sliding index an hour after the start of the fixed series


        keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
        maxes = []
        offsets = []
        averages = []

        for k in keys:
            store = []
            for n in range(20): # Calculate a coefficient over a 30 min window
                coef = np.corrcoef(fixed[k][j:j+60], sliding[k][sliding_start-n:sliding_stop-n])[0, 1]
                store.append(coef) # Append the storage arrays
            maxes.append(max(store, key=abs))
            offsets.append(store.index(max(store, key=abs)))
            averages.append(np.average(fixed[k][j:j+60]))

        rows.append(np.concatenate(([fixed['Time'][j]], [fixed['Time'][j+60]], maxes, offsets, averages), axis=None))

    return rows # Output the entire chunk of metadata

sat1 = input('Enter the first (sliding) satellite to correlate ("themis" or "artemis"): ')
sat2 = input('Enter the first (fixed) satellite to correlate ("themis" or "omni"): ')
eventSelector = input('Enter the file date to correlate (in yyyy-mm-dd_hh-mm format) or type "all" to correlate the whole folder: ')


if sat1 == 'artemis':
    sat1Directory = '../metadata/Artemis/'
    sat1Name = 'Artemis'
elif sat1 == 'themis':
    sat1Directory = '../metadata/Themis/'
    sat1Name = 'Themis'
else:
    raise ValueError('String "{}" is not one of ("themis", "artemis")'.format(sat1))

if sat2 == 'themis' and sat1 != 'themis':
    sat2Directory = '../metadata/Themis/'
    sat2Name = 'Themis'
elif sat2 == 'omni':
    sat2Directory = '../metadata/Omni/'
    sat2Name = 'Omni'
elif sat1 == 'themis' and sat2 == 'themis':
    raise ValueError('Both satellite 1 and satellite 2 can not be "themis"')
else:
    raise ValueError('String "{}" is not one of ("themis", "omni")'.format(sat2))

if eventSelector == 'all':
    sat1Files = [filename for filename in os.listdir(sat1Directory)]
    sat2Files = [filename for filename in os.listdir(sat2Directory)]

    for (i,j) in zip(sat1Files, sat2Files):
        sat1Data = pd.read_csv(sat1Files[i], delimiter=',', header=0)
        sat1Data['Time'] = pd.to_datetime(sat1Data['Time'], format='%Y-%m-%d %H:%M:%S')

        sat2Data = pd.read_csv(sat2Files[j], delimiter=',', header=0)
        sat2Data['Time'] = pd.to_datetime(sat2Data['Time'], format='%Y-%m-%d %H:%M:%S')

        eventMetadata = pd.DataFrame(correlate(sat1Data, sat2Data), columns=['Start', 'Stop', 'P(Bx)', 'P(By)', 'P(Bz)', 'P(Vx)', 'P(Vy)', 'P(Vz)', 'P(n)', 'P(T)', 'Offset (Bx)', 'Offset (By)', 'Offset (Bz)', 'Offset (Vx)', 'Offset (Vy)', 'Offset (Vz)', 'Offset (n)', 'Offset (T)', 'Avg Bx', 'Avg By', 'Avg Bz', 'Avg Vx', 'Avg Vy', 'Avg Vz', 'Avg n', 'Avg T'])
        eventMetadata.to_csv('../metadata/{}-{}'.format(sat1, sat2Files[j]))


else:
    sat1Data = pd.read_csv(os.path.join(sat1Directory, '{}_{}.csv'.format(sat1Name, eventSelector)), delimiter=',', header=0)
    sat1Data['Time'] = pd.to_datetime(sat1Data['Time'], format='%Y-%m-%d %H:%M:%S')

    sat2Data = pd.read_csv(os.path.join(sat2Directory, '{}_{}.csv'.format(sat2Name, eventSelector)), delimiter=',', header=0)
    sat2Data['Time'] = pd.to_datetime(sat2Data['Time'], format='%Y-%m-%d %H:%M:%S')

    eventMetadata = pd.DataFrame(correlate(sat1Data, sat2Data), columns=['Start', 'Stop', 'P(Bx)', 'P(By)', 'P(Bz)', 'P(Vx)', 'P(Vy)', 'P(Vz)', 'P(n)', 'P(T)', 'Offset (Bx)', 'Offset (By)', 'Offset (Bz)', 'Offset (Vx)', 'Offset (Vy)', 'Offset (Vz)', 'Offset (n)', 'Offset (T)', 'Avg Bx', 'Avg By', 'Avg Bz', 'Avg Vx', 'Avg Vy', 'Avg Vz', 'Avg n', 'Avg T'])
    eventMetadata.to_csv('../metadata/{}_{}_{}.csv'.format(sat1Name, sat2Name, eventSelector))
