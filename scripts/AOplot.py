import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
import os

def mape(artemis, omni):
    #m = (1/60) * (np.average([((a-o)/a) for o, a in zip(omni.to_numpy(), artemis.to_numpy())]))
    m=1
    return m
def scatterplot(ax, x, y):
    ax.set_ylim(-1,1)
    ax.set_xlim(0, 30)
    ax.hlines(0, 0, 30, color='black', linestyle='dashed')
    ax.scatter(x, y)
    plt.suptitle('Comparison of Correlation Metrics')
    plt.tight_layout()
def correlate(artemis, omni, workingDir):
    numWindows = len(omni)-59

    for n in range(numWindows):
        windowCounter = 0
        aStart = (artemis.loc[artemis['Time'] == omni['Time'][n]]).index[0]
        aStop = (artemis.loc[artemis['Time'] == omni['Time'][n + 59]]).index[0]
        keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']

        for k in keys:
            rStore = []
            rhoStore = []
            tauStore = []
            mStore = []

            rMax = []
            rhoMax = []
            tauMax = []
            mMax = []

            for i in range(31):
                rStore.append(pearsonr(omni[k][n:n+59], artemis[k][aStart-n:aStop-n])[0])
                rhoStore.append(spearmanr(omni[k][n:n+59], artemis[k][aStart-n:aStop-n])[0])
                tauStore.append(kendalltau(omni[k][n:n+59], artemis[k][aStart-n:aStop-n])[0])
                mStore.append(mape(omni[k][n:n+59], artemis[k][aStart-n:aStop-n]))

            for corrs, maxes in zip([rStore, rhoStore, tauStore, mStore], [rMax, rhoMax, tauMax, mMax]):
                if all(c < 0 for c in corrs[1:]):
                    maxes.extend([max(corrs[1:], key=abs), corrs.index(max(corrs[1:], key=abs))])
                else:
                    maxes.extend([max(corrs[1:]), corrs.index(max(corrs[1:]))])

            fig, ((p1, r1, t1, m1), (p2, r2, t2, m2)) = plt.subplots(nrows=2, ncols=4, figsize=(35,8))
            for axs, vars in zip([p1, r1, t1, m1],[rStore, rhoStore, tauStore, mStore]):
                scatterplot(axs, np.arange(0, 31, 1), vars)
            if os.path.exists(os.path.join(workingDir, 'output-data/correlation-plots/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k))):
                plt.savefig(os.path.join(workingDir, 'output-data/correlation-plots/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M-%S'))), dpi=300)
            else:
                os.makedirs(os.path.join(workingDir, 'output-data/correlation-plots/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
                plt.savefig(os.path.join(workingDir, 'output-data/correlation-plots/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M-%S'))), dpi=300)
            plt.close()

        windowCounter = windowCounter + 1
        print('Computing window {} of {}...'.format(windowCounter, numWindows))

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
    print('All files')
elif int(toCorrelate) < len(omniFileList):
    artemisData = pd.read_csv(os.path.join(artemisDirectory, artemisFileList[int(toCorrelate)]), delimiter=',', header=0)
    omniData = pd.read_csv(os.path.join(omniDirectory, omniFileList[int(toCorrelate)]), delimiter=',', header=0)
    artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
    omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')
    correlate(artemisData, omniData, projDir)
else:
    raise ValueError('Must be "any" or less than {}'.format(len(fileList)))
