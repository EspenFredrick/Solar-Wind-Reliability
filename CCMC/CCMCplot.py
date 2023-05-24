import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

file1Path = sys.argv[1]
legend1 = sys.argv[2]
file2Path = sys.argv[3]
legend2 = sys.argv[4]
varToPlot = sys.argv[5]

outputPath = sys.argv[6]

print(varToPlot)

if varToPlot == 'JH':
    file1 = pd.read_csv(file1Path, delim_whitespace=True, comment='#', index_col=False, header=None, dtype={0:int, 1:int, 2:int, 3:int, 4:int, 5:int}, names=['Year', 'Month', 'Day', 'Hour', 'Min', 'Sec', 'JH_N', 'I_N', 'DP_N', 'JH_S', 'I_S', 'DP_S', 'W_N', 'W_S'])
    file2 = pd.read_csv(file2Path, delim_whitespace=True, comment='#', index_col=False, header=None, dtype={0:int, 1:int, 2:int, 3:int, 4:int, 5:int}, names=['Year', 'Month', 'Day', 'Hour', 'Min', 'Sec', 'JH_N', 'I_N', 'DP_N', 'JH_S', 'I_S', 'DP_S', 'W_N', 'W_S'])

elif varToPlot == 'CPCP':
    file1 = pd.read_csv(file1Path, delim_whitespace=True, comment='#', index_col=False, header=None, dtype={0:int, 1:int, 2:int, 3:int, 4:int, 5:int}, names=['Year', 'Month', 'Day', 'Hour', 'Min', 'Sec', 'mSec', 'CPCP_N', 'CPCP_S', 'DST', 'CPCP_N2', 'CPCP_S2'])
    file2 = pd.read_csv(file2Path, delim_whitespace=True, comment='#', index_col=False, header=None, dtype={0:int, 1:int, 2:int, 3:int, 4:int, 5:int}, names=['Year', 'Month', 'Day', 'Hour', 'Min', 'Sec', 'mSec', 'CPCP_N', 'CPCP_S', 'DST', 'CPCP_N2', 'CPCP_S2'])

else:
    raise ValueError("Not one of 'JH' (Joule heating) or 'CPCP' (Cross-polar cap potential).")


file1['Time'] = pd.to_datetime(file1['Year'].astype(str)+file1['Month'].astype(str)+file1['Day'].astype(str)+file1['Hour'].astype(str)+file1['Min'].astype(str)+file1['Sec'].astype(str), format='%Y%m%d%H%M%S')
file2['Time'] = pd.to_datetime(file2['Year'].astype(str)+file2['Month'].astype(str)+file2['Day'].astype(str)+file2['Hour'].astype(str)+file2['Min'].astype(str)+file2['Sec'].astype(str), format='%Y%m%d%H%M%S')

xLabel = input("X-label for plot: ")
yLabel = input("Y-label for plot: ")
title = input("Title of plot: ")

fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(8,6), sharex=True)
plt.subplots_adjust(hspace=0)
ax0.plot(file1['Time'], file1['{}_N'.format(varToPlot)], label=legend1, color='C2')
ax0.plot(file2['Time'], file2['{}_N'.format(varToPlot)], label=legend2, color='C4')
ax0.legend(loc='lower right')
ax0.set_ylabel('{}, North'.format(yLabel))
ax0.set_xlim((file1['Time'][0], file1['Time'][len(file1['Time'])-1]))

ax1.plot(file1['Time'], file1['{}_S'.format(varToPlot)], label=legend1, color='C2')
ax1.plot(file2['Time'], file2['{}_S'.format(varToPlot)], label=legend2, color='C4')
ax1.legend(loc='lower right')
ax1.set_ylabel('{}, South'.format(yLabel))
ax1.set_xlabel(xLabel)
ax1.set_xlim((file1['Time'][0], file1['Time'][len(file1['Time'])-1]))

ax1.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=8))
ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax0.xaxis.get_major_locator()))
ax0.set_title(title)
plt.savefig(str(outputPath), dpi=300)
