'''
This script is used to import a list of times and identify whether the resulting solar wind profile contains one of the following:
    - High Speed Streams
    - Slow Solar Wind
    - ICMEs (interplanetary coronal mass ejections)
The script imports a list of events when ARTEMIS was near the Earth-Sun line and compares the density and fluctuations in the magnetic field.
The output is a similarly formatted CSV file that contains boolean values identifying whether the structure exists.
'''

import numpy as np
import pandas as pd
import os

def identify(data):
    numWindows = len(data)-179
    dBB = []
    for n in range(numWindows):
        dBB.append(data['BZ_GSE'][n+90] / np.average(data['BZ_GSE'][n:n+180]))

    if np.average(dBB) > 1 and np.average(data['Vx']) > 500 and np.average(data['proton_density']) < 3:
        print('High-Speed Stream')
    elif np.average(dBB) < 1 and np.average(data['Vx']) < 500 and  np.average(data['proton_density']) > 3:
        print('Slow Solr Wind')
    else:
        print('Something else TBD')

projDir ='/Volumes/Research/' # Change to your own project directory!!!!!! <--------- Important!
eventDirectory = os.path.join(projDir, 'Solar-Wind-Reliability/output-data/GSE/Omni/')
fileList = sorted(filter(lambda x: os.path.isfile(os.path.join(eventDirectory, x)), os.listdir(eventDirectory)))

for l in range(len(fileList)):
    if not fileList[l].startswith('.') and not 'copy' in fileList[l]:
        omniData = pd.read_csv(os.path.join(eventDirectory, fileList[l]), delimiter=',', header=0)
        omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')
        if len(omniData['Time']) >= 180:
            print('Identifying SW type for {}...'.format(fileList[l]))
            identify(omniData)