import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
import os

def meanAbsPercErr(artemis, omni):
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

def correlate(artemis, omni, workingDir='/Volumes/Research', r=True, rho=True, tau=True, makePlots = True):
    numWindows = len(omni)-59
    windowCounter = 0

    for n in range(numWindows):
        nplus = n + 1
        print('Computing window {} of {}...'.format(nplus, numWindows))

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
                rStore.append(pearsonr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0])
                rhoStore.append(spearmanr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0])
                tauStore.append(kendalltau(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0])
                mStore.append(meanAbsPercErr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i]))

            for corrs, maxes in zip([rStore, rhoStore, tauStore, mStore], [rMax, rhoMax, tauMax, mMax]):
                if all(c < 0 for c in corrs[1:]):
                    maxes.extend([max(corrs[1:], key=abs), corrs.index(max(corrs[1:], key=abs))])
                else:
                    maxes.extend([max(corrs[1:]), corrs.index(max(corrs[1:]))])

            fig, ((p1, r1, t1, m1), (p2, r2, t2, m2)) = plt.subplots(nrows=2, ncols=4, figsize=(35,8))
            for axs, vars in zip([p1, r1, t1, m1],[rStore, rhoStore, tauStore, mStore]):
                scatterplot(axs, np.arange(0, 31, 1), vars)

            if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k))):
                plt.savefig(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))), dpi=300)
            else:
                os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
                plt.savefig(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))), dpi=300)
            plt.close()
    print('Done.')