'''
This script takes the time shift for every hour interval by correlation coefficient and by slope, and plots ARTEMIS and OMNI on top of each other.
It also generates the scatter plot of ARTEMIS as a function of OMNI shifted by the slope closest to 1 and fits a curve through it, giving the slope and the intercept
'''

#Import statements:
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator
import os

def makeScatter(x, y):
    fig = plt.figure(figsize=(6, 10), constrained_layout=True)

    gridspec = fig.add_gridspec(nrows=9, ncols=5)
    axes = {}
    axes['shiftByCorr'] = fig.add_subplot(gridspec[0:2, 0:5])
    axes['shiftBySlope'] = fig.add_subplot(gridspec[2:4, 0:5])
    axes['scatterPlot'] = fig.add_subplot(gridspec[4:9, 0:5])

    axes['scatterPlot'].plot(x, y)
    plt.show()

makeScatter([1,2,3], [4,5,6])








'''
projDir ='/Volumes/Research'
artemisDataDirectory = os.path.join(projDir, 'Solar-Wind-Reliability/output-data/GSE/Artemis/')
omniDataDirectory = os.path.join(projDir, 'Solar-Wind-Reliability/output-data/GSE/Omni/')
omniFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(omniDataDirectory, x)), os.listdir(omniDataDirectory)))
artemisFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(artemisDataDirectory, x)), os.listdir(artemisDataDirectory)))
'''