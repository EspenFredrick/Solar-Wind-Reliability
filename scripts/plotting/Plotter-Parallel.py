import concurrent.futures
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, linregress
import os

# Find slope closest to _...
def closestTo(inputList, val):
  arr = np.asarray(inputList)
  i = (np.abs(arr - val)).argmin()
  return arr[i]

# Correlation metrics
def corrMetrics(omni, artemis):
    mape = (1/60) * (np.sum([abs(((a - o)/a)) for o, a in zip(omni, artemis)]))
    ratio = np.average([(abs(o - a) / abs(a)) for o, a in zip(omni, artemis)])
    rmse = np.sqrt(np.sum([((a - o) ** 2) / 60 for o, a in zip(omni, artemis)]))
    rmseArtemis = np.sqrt(np.sum([((a - o) ** 2) / (a ** 2) if a != 0 else 0 for o, a in zip(omni, artemis)]) / 60)
    rmseOmni = np.sqrt(np.sum([((a - o) ** 2) / (o ** 2) if o != 0 else 0 for o, a in zip(omni, artemis)]) / 60)
    rmseAverage = np.sqrt(np.sum([((a - o) ** 2) / (((a + o) / 2) ** 2) for o, a in zip(omni, artemis)]) / 60)

    slope, intercept, rvalue, pvalue, stderr = linregress(artemis, omni)

    return mape, ratio, rmse, rmseArtemis, rmseOmni, rmseAverage, slope

# Function to create the scatter plots for each metric
def scatterplot(ax, x, y):
    ax.set_ylim(-1,1)
    ax.set_xlim(0, 30)
    ax.hlines(0, 0, 30, color='black', linestyle='dashed')
    ax.set_xlabel('Time Shift (min)')
    ax.set_ylabel('Correlation Value')
    ax.scatter(x, y)
    ax.xaxis.set_minor_locator(MultipleLocator(1))

# Function to create the line plots for each metric. This visualizes how they shift relative to another at peak correlation.
def lineplot(ax, x, omniLine, artemisLine, unit):
    ax.set_ylim(2*min(omniLine), 2*abs(max(omniLine)))
    ax.set_xlim(min(x), max(x))
    ax.set_xlabel('Time UTC')
    ax.set_ylabel(unit)
    ax.plot(x, omniLine, label='OMNI')
    ax.plot(x, artemisLine, label='Artemis')
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter('%H:%M'))
    ax.legend(loc='lower right')

# Function to compute the correlation metrics.
def correlate(artemis, omni, workingDir='/Volumes/Research'):
    numWindows = len(omni)-59 # Number of 1-hour blocks in the data set

    for n in range(numWindows): # Loop over each block
        print('Computing window {} of {}...'.format(n+1, numWindows))

        # Find the start and stop index in Artemis that matches the nth and n+59th window of Omni
        aStart = (artemis.loc[artemis['Time'] == omni['Time'][n]]).index[0]
        aStop = (artemis.loc[artemis['Time'] == omni['Time'][n+59]]).index[0]

        # Variables to loop over and their respective units
        keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
        units = [r'$B_x$ (nT)', r'$B_y$ (nT)', r'$B_z$ (nT)', r'$V_x$ (km/s)', r'$V_y$ (km/s)', r'$V_z$ (km/s)', r'Density ($cm^{-3}$)', 'Temperature (K)']

        for k, u in zip(keys, units):
            print('Key {}...'.format(k))

            # Initialize empty storage arrays for each metric
            pearsonStore = []
            mapeStore = []
            ratioStore = []
            rmseStore = []
            artemisStore = []
            omniStore = []
            avgStore = []

            slopeStore = []

            # Initialize arrays which store the maximum metric value and its index
            pearsonMax = []
            mapeMin = []
            ratioMin = []
            rmseMin = []
            artemisMin = []
            omniMin = []
            avgMin = []

            slopeClosestToOne = []

            # Slide Artemis 30 times (for a 30-minute shift) over the Omni set and append the metric to each array
            for i in range(31):
                corrcoef = pearsonr(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])[0]
                mape, ratio, rmse, rmseArtemis, rmseOmni, rmseAverage, slopeInt = corrMetrics(omni[k][n:n+59], artemis[k][aStart-i:aStop-i])

                for vals, lists in zip([corrcoef, mape, ratio, rmse, rmseArtemis, rmseOmni, rmseAverage, slopeInt], [pearsonStore, mapeStore, ratioStore, rmseStore, artemisStore, omniStore, avgStore, slopeStore]):
                    lists.append(vals)

            # Store the maximum Pearson correlation coef. in position 0, and the index at which it occurs (time shift) in position 1
            if all(c < 0 for c in pearsonStore[1:]):
                pearsonMax.extend([max(pearsonStore[1:], key=abs), pearsonStore.index(max(pearsonStore[1:], key=abs))])
            else:
                pearsonMax.extend([max(pearsonStore[1:]), pearsonStore.index(max(pearsonStore[1:]))])

            # Store the minimum values for the other correlations in position 0 and the index at which it occurs in position 1
            for corrs, mins in zip([mapeStore, ratioStore, rmseStore, artemisStore, omniStore, avgStore], [mapeMin, ratioMin, rmseMin, artemisMin, omniMin, avgMin]):
                mins.extend([min(corrs[1:]), corrs.index(min(corrs[1:]))])

            #Store the slope closest to 1
            slopeClosestToOne.extend([closestTo(slopeStore[1:], 1), slopeStore.index(closestTo(slopeStore[1:], 1))])

            # Initialize the scatter plots and line plots. Top row are scatter plots, bottom row are line plots
            fig, ((p1, m1, s1, r1), (p2, m2, s2, r2), (rmse1, rmseA1, rmseO1, rmseAvg1), (rmse2, rmseA2, rmseO2, rmseAvg2)) = plt.subplots(nrows=4, ncols=4, figsize=(18,10))

            # Run the scatter plot and function to plot how the metric changes
            # Create a vertical line to the maximum metric value and highlight it red

            for axs, vars, minmax, labels in zip([p1, m1, s1, r1, rmse1, rmseA1, rmseO1, rmseAvg1], [pearsonStore, mapeStore, slopeStore, ratioStore, rmseStore, artemisStore, omniStore, avgStore], [pearsonMax, mapeMin, slopeClosestToOne, ratioMin, rmseMin, artemisMin, omniMin, avgMin], ['Pearson R', 'MAPE', 'Slope', 'Ratio (normalized to Artemis)', 'RMSE', 'RMSE Norm. Artemis', 'RMSE Norm. Omni', 'RMSE Norm. avg. Artemis/Omni']):
                axs.set_ylim(0, max(vars)+1)
                p1.set_ylim(-1, 1)
                s1.set_ylim(-2, 2)
                axs.set_xlim(0, 30)
                axs.set_xlabel('Time Shift (min)')
                axs.set_ylabel('Correlation Value')
                axs.scatter(np.arange(0, 31, 1), vars)
                axs.scatter(minmax[1], minmax[0], color='red')
                axs.vlines(minmax[1], -2, minmax[0], color='red', linestyle='dashed')
                if axs == p1:
                    axs.text(.01, .99, 'Max. = {}'.format(round(minmax[0], 3)), ha='left', va='top',transform=axs.transAxes)
                elif axs == s1:
                    axs.text(.01, .99, 'Slope closest to 1 = {}'.format(round(minmax[0], 3)), ha='left', va='top',transform=axs.transAxes)
                else:
                    axs.text(.01, .99, 'Min. = {}'.format(round(minmax[0], 3)), ha='left', va='top', transform=axs.transAxes)
                axs.xaxis.set_minor_locator(MultipleLocator(1))
                axs.set_title(labels)

            # Run the line plot function to plot how Artemis shifted by the time offset lines up
            for axs2, minmax in zip([p2, m2, s2, r2, rmse2, rmseA2, rmseO2, rmseAvg2], [pearsonMax, mapeMin, slopeClosestToOne, ratioMin, rmseMin, artemisMin, omniMin, avgMin]):
                lineplot(axs2, omni['Time'][n:n+60], omni[k][n:n+60], artemis[k][aStart-minmax[1]:aStop-minmax[1]+1], u)
                axs2.set_title('Time Series Shift by Metric')
                axs2.text(.01, .99, 'Shift = {} min.'.format(round(minmax[1], 3)), ha='left', va='top', transform=axs2.transAxes)
            plt.suptitle('Comparison of Correlation Metrics', fontsize=18)
            plt.tight_layout()

            # Save images to directory
            if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots-parallel/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k))):
                plt.savefig(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots-parallel/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))), dpi=300)
            else:
                os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots-parallel/{}/{}/'.format(omni['Time'][n].strftime('%Y-%m-%d'), k)))
                plt.savefig(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/correlation-plots-parallel/{}/{}/{}.png'.format(omni['Time'][n].strftime('%Y-%m-%d'), k, omni['Time'][n].strftime('%H-%M'))), dpi=300)
            plt.close()
    print('Done.')

def process_file(omni_file, artemis_file, artemis_directory, omni_directory, proj_dir):
    print(f'Correlating {omni_file}...')
    artemis_data = pd.read_csv(os.path.join(artemis_directory, artemis_file), delimiter=',', header=0)
    omni_data = pd.read_csv(os.path.join(omni_directory, omni_file), delimiter=',', header=0)
    artemis_data['Time'] = pd.to_datetime(artemis_data['Time'], format='%Y-%m-%d %H:%M:%S')
    omni_data['Time'] = pd.to_datetime(omni_data['Time'], format='%Y-%m-%d %H:%M:%S')

    correlate(artemis_data, omni_data, proj_dir)

def main():
    proj_dir = '/Volumes/Research'
    artemis_directory = os.path.join(proj_dir, 'Solar-Wind-Reliability/output-data/GSE/Artemis/')
    omni_directory = os.path.join(proj_dir, 'Solar-Wind-Reliability/output-data/GSE/Omni/')

    omni_file_list = sorted(filter(lambda x: os.path.isfile(os.path.join(omni_directory, x)),
                                   os.listdir(omni_directory)))
    artemis_file_list = sorted(filter(lambda x: os.path.isfile(os.path.join(artemis_directory, x)),
                                      os.listdir(artemis_directory)))

    for nums, files in enumerate(omni_file_list):
        print('{} - {}'.format(nums, files))

    to_correlate = input('Please enter the number of the file you wish to correlate, or type "all" to correlate the whole folder: ')

    with concurrent.futures.ProcessPoolExecutor() as executor:
        if to_correlate == 'all':
            futures = [executor.submit(process_file, omni_file, artemis_file, artemis_directory, omni_directory, proj_dir) for omni_file, artemis_file in zip(omni_file_list, artemis_file_list) if not omni_file.startswith('.')]
            concurrent.futures.wait(futures)
        elif int(to_correlate) < len(omni_file_list):
            omni_file = omni_file_list[int(to_correlate)]
            artemis_file = artemis_file_list[int(to_correlate)]
            process_file(omni_file, artemis_file, artemis_directory, omni_directory, proj_dir)
        else:
            raise ValueError('Must be "any" or less than {}'.format(len(omni_file_list)))

if __name__ == "__main__":
    main()

'''
def process_files(file_pair):
    # Your existing script logic that reads, compares, computes values, and makes plots
    file1, file2 = file_pair
    # ... rest of your script ...

if __name__ == "__main__":
    # List of file pairs to process
    file_pairs = [(file1_path, file2_path), (file3_path, file4_path), ...]

    # Adjust the number of processes as needed
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        # Submit tasks for each file pair
        futures = [executor.submit(process_files, file_pair) for file_pair in file_pairs]

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
'''