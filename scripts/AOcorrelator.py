import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
import os

def correlate(artemis, omni, workingDir='/Volumes/Research', r=True, rho=True, tau=True, makePlots = True):
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
                if
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