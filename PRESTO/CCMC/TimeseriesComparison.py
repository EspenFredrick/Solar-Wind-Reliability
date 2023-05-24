import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

labels = ['Year', 'Month', 'Day', 'Hour', 'Min', 'Sec' ,'Bx', 'By', 'Bz', 'Vx', 'Vy', 'Vz', 'n', 'T']
CCMC_Omni_20191127_SWMF = pd.read_csv('../../CCMC/Omni_20191127_SWMF.txt', sep=' ', index_col=None, header=None, parse_dates={'Time' : [0, 1, 2, 3, 4, 5]})
#CCMC_Omni_20191127_SWMF['Year'].astype(str)
CCMC_Omni_20191127_SWMF['Time']= pd.to_datetime(CCMC_Omni_20191127_SWMF['Time'], format='%Y %m %d %H %M %S')

print(CCMC_Omni_20191127_SWMF)
#plt.plot(CCMC_Omni_20191127_SWMF['Time'], CCMC_Omni_20191127_SWMF['Bz'])