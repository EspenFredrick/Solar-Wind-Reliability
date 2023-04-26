import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator



def correlate(sliding, fixed, sat1Name, sat2Name):
    dataRows = []
    numWindows = len(fixed['Time']) - 59

    for j in range(numWindows): # Find the correlation coefficient over 'numWindows' hour-intervals
        sliding_start = (sliding.loc[sliding['Time'] == fixed['Time'][j]]).index[0] # Set the start time of the sliding index where the timestamp of the fixed series begins
        sliding_stop = (sliding.loc[sliding['Time'] == fixed['Time'][j+59]]).index[0] # Set the end of the sliding index an hour after the start of the fixed series

        keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
        pMaxes = []
        ratioMaxes = []
        pOffsets = []
        ratioOffsets = []

        for k in keys:
            fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, ncols=1, figsize=(8, 10))
            corrStore = [] # Temp storage array for coefficients
            avgStore = []

            for n in range(31): # Calculate a coefficient over a 0 to 30-min window
                corrStore.append(np.corrcoef(fixed[k][j:j+59], sliding[k][sliding_start-n:sliding_stop-n])[0, 1])  # Append the storage arrays
                avgStore.append(np.average([min(i, j, key=abs) / max(i, j, key=abs) for i, j in zip(sliding[k][sliding_start - n:sliding_stop - n].to_numpy(), fixed[k][j:j + 60].to_numpy())]))

            ax1.scatter(np.arange(0, 31, 1), corrStore, color='C0')
            ax1.scatter(np.arange(0, 31, 1), avgStore, color='C1')

            if all(corrs < 0 for corrs in corrStore[1:]):
                    pMaxes.append(max(corrStore[1:], key=abs))
                    pOffsets.append(corrStore.index(max(corrStore[1:], key=abs)))
                    pShift = corrStore.index(max(corrStore[1:], key=abs))
                    pMaxLineHeight = max(corrStore[1:], key=abs)
            else:
                    pMaxes.append(max(corrStore[1:]))
                    pOffsets.append(corrStore.index(max(corrStore[1:])))
                    pShift = corrStore.index(max(corrStore[1:]))
                    pMaxLineHeight = max(corrStore[1:])

            ratioMaxes.append(max(avgStore[1:]))
            ratioOffsets.append(avgStore.index(max(avgStore[1:])))
            rShift = avgStore.index(max(avgStore[1:]))

            ax1.vlines(pShift, 0, pMaxLineHeight, linestyle='dashed', color='C0')
            ax1.vlines(rShift, 0, max(avgStore), linestyle='dashed', color='C1')

            ax2.plot(fixed['Time'][j:j + 59], sliding[k][sliding_start-pShift : sliding_stop-pShift], label=sat1Name)
            ax2.plot(fixed['Time'][j:j + 59], fixed[k][j:j + 59], label=sat2Name)

            ax3.plot(fixed['Time'][j:j + 59], sliding[k][sliding_start-rShift : sliding_stop-rShift], label=sat1Name)
            ax3.plot(fixed['Time'][j:j + 59], fixed[k][j:j + 59], label=sat2Name)

            ax4.plot(sliding['Time'], sliding[k], label=sat1Name)
            ax4.plot(fixed['Time'], fixed[k], label=sat2Name)

            ax1.hlines(0, 0, 30, color='black')
            ax1.set_ylim(-1, 1)
            ax1.set_xlim(0, 30)
            ax1.set_title("Peak Corr. Coef./Hourly Ratio")
            ax1.set_ylabel("Correlation Coefficient", color='C0')
            ax1.set_xlabel("Timeshift (min)")
            ax1.xaxis.set_minor_locator(AutoMinorLocator())
            axr = ax1.twinx()
            axr.set_ylim(-1, 1)
            axr.set_ylabel("Avg. Ratio of Series ({})".format(k), color='C1')
            ax2.set_title("Shifted Series by Corr. Coef.")
            ax2.set_ylabel(k)
            ax2.set_xlabel("Time UTC")
            ax2.set_xlim(fixed['Time'][j], fixed['Time'][j + 59])
            ax2.xaxis.set_minor_locator(AutoMinorLocator())
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax3.set_title("Shifted Series by Hourly Ratio")
            ax3.set_ylabel(k)
            ax3.set_xlabel("Time UTC")
            ax3.set_xlim(fixed['Time'][j], fixed['Time'][j + 59])
            ax3.xaxis.set_minor_locator(AutoMinorLocator())
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax4.set_title("Artemis/Omni Time Series")
            ax4.set_ylabel(k)
            ax4.set_xlabel("Time UTC")
            ax4.set_xlim(fixed['Time'][0], fixed['Time'][len(fixed['Time'])-1])
            ax4.xaxis.set_minor_locator(AutoMinorLocator())
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

            ax4.legend(loc='lower right')
            plt.tight_layout()

            if os.path.exists('../metadata/plots/{}-{}_{}/{}/'.format(sat1Name, sat2Name, fixed['Time'][j].strftime('%Y-%m-%d'), k)):
                plt.savefig('../metadata/plots/{}-{}_{}/{}/{}-{}_{}.png'.format(sat1Name, sat2Name, fixed['Time'][j].strftime('%Y-%m-%d'), k, sat1Name, sat2Name, fixed['Time'][j].strftime('%H-%M-%S')), dpi=300)
            else:
                os.makedirs('../metadata/plots/{}-{}_{}/{}/'.format(sat1Name, sat2Name, fixed['Time'][j].strftime('%Y-%m-%d'), k))
                plt.savefig('../metadata/plots/{}-{}_{}/{}/{}-{}_{}.png'.format(sat1Name, sat2Name, fixed['Time'][j].strftime('%Y-%m-%d'), k, sat1Name, sat2Name, fixed['Time'][j].strftime('%H-%M-%S')), dpi=300)
            plt.close()

eventSelector = input('Enter the file date to correlate (in yyyy-mm-dd_hh-mm format): ')
sat1Directory = '../metadata/Artemis/'
sat1Name = 'Artemis'
sat2Directory = '../metadata/Omni/'
sat2Name = 'Omni'

sat1Data = pd.read_csv(os.path.join(sat1Directory, '{}_{}.csv'.format(sat1Name, eventSelector)), delimiter=',', header=0)
sat1Data['Time'] = pd.to_datetime(sat1Data['Time'], format='%Y-%m-%d %H:%M:%S')
sat2Data = pd.read_csv(os.path.join(sat2Directory, '{}_{}.csv'.format(sat2Name, eventSelector)), delimiter=',', header=0)
sat2Data['Time'] = pd.to_datetime(sat2Data['Time'], format='%Y-%m-%d %H:%M:%S')

correlate(sat1Data, sat2Data, sat1Name, sat2Name)