import numpy as np
import pandas as pd
from scipy.stats import pearsonr, linregress
import os
from concurrent.futures import ProcessPoolExecutor
import time

# Correlation metrics
def corrMetrics(omni, artemis):
    ratio = np.mean(np.abs(omni - artemis) / np.abs(artemis))
    rmse = np.sqrt(np.mean((artemis - omni) ** 2))
    rmse_Artemis = np.sqrt(np.sum([((a - o) ** 2) / (a ** 2) if a != 0 else 0 for o, a in zip(omni, artemis)]) / 60)
    rmse_Omni = np.sqrt(np.sum([((a - o) ** 2) / (o ** 2) if o != 0 else 0 for o, a in zip(omni, artemis)]) / 60)
    rmse_Average = np.sqrt(np.mean((artemis - omni) ** 2 / (((artemis + omni) / 2) ** 2)))
    slope, intercept, *_ = linregress(artemis, omni)
    return ratio, rmse, rmse_Artemis, rmse_Omni, rmse_Average, slope, intercept

def calculate_metrics(omni_slice, artemis_slice):
    corrcoef, _ = pearsonr(omni_slice, artemis_slice)
    ratio, rmse, rmseArtemis, rmseOmni, rmseAverage, slopes, ints = corrMetrics(omni_slice, artemis_slice)
    return corrcoef, ratio, rmse, rmseArtemis, rmseOmni, rmseAverage, slopes, ints

def find_max_value_and_index(values):
    if all(c < 0 for c in values[1:]):
        return max(values[1:], key=abs), values.index(max(values[1:], key=abs))
    else:
        return max(values[1:]), values.index(max(values[1:]))

def find_min_value_and_index(values):
    return min(values[1:]), values.index(min(values[1:]))

def find_closest_to(inputList, val):
    return inputList[np.argmin(np.abs(np.array(inputList) - val))], np.argmin(np.abs(np.array(inputList) - val))

# Function to compute the correlation metrics.
def correlate(file_pair, workingDir):
    artemisData, omniData = file_pair

    artemis = pd.read_csv(artemisData, delimiter=',', header=0)
    omni = pd.read_csv(omniData, delimiter=',', header=0)

    artemis['Time'] = pd.to_datetime(artemis['Time'], format='%Y-%m-%d %H:%M:%S')
    omni['Time'] = pd.to_datetime(omni['Time'], format='%Y-%m-%d %H:%M:%S')


    # Variables to loop over and their respective units
    keys = ['BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']
    num_windows = len(omni)-60 # Number of 1-hour blocks in the data set

    for k in keys:
        print(f'Key {k}: Computing {num_windows} windows...')
        data_rows = []
        offset_rows = []

        for n in range(num_windows): # Loop over each block
            a_start = artemis.loc[artemis['Time'] == omni['Time'].iloc[n]].index[0]
            a_stop = artemis.loc[artemis['Time'] == omni['Time'].iloc[n + 60]].index[0]
            hourly_velocity = np.average(omni['Vx'][n:n+60])

            # Initialize arrays to store metrics
            metric_names = ['Pearson', 'Ratio', 'RMSE', 'RMSE Artemis', 'RMSE Omni', 'RMSE Average', 'Slopes', 'Intercepts']
            metric_stores = {name: [] for name in metric_names}
            target_stores = {name + ' Target': [] for name in metric_names}

            for i in range(31):
                omni_slice = omni[k][n:n + 60]
                artemis_slice = artemis[k][a_start - i:a_stop - i]

                values = calculate_metrics(omni_slice, artemis_slice)
                for count, (metric, store) in enumerate(metric_stores.items()):
                    store.append(values[count])

            pearson_max_value, pearson_max_index = find_max_value_and_index(metric_stores['Pearson'])
            target_stores['Pearson Target'] = [pearson_max_value, pearson_max_index]

            for name, store in metric_stores.items():
                if name not in ['Pearson', 'Slopes', 'Intercepts']:
                    min_value, min_index = find_min_value_and_index(store)
                    target_stores[name + ' Target'].extend([min_value, min_index])

            slope_closest_to_one, slope_index = find_closest_to(metric_stores['Slopes'], 1)
            intercept_for_slope = metric_stores['Intercepts'][slope_index]
            target_stores['Slopes Target'] = [slope_closest_to_one, slope_index]
            target_stores['Intercepts'] = [intercept_for_slope, slope_index]

            data_rows.append(np.concatenate(([omni['Time'][n]], [omni['Time'][n+60]], *[store[0] for name, store in metric_stores.items()], hourly_velocity), axis=None))
            offset_rows.append(np.concatenate(([omni['Time'][n]], [omni['Time'][n+60]], *[store[1] for name, store in metric_stores.items()]), axis=None))

        event_metadata = pd.DataFrame(data_rows, columns=['Start', 'Stop','Pearson', 'Ratio', 'RMSE', 'RMSE_Artemis', 'RMSE_Omni', 'RMSE_Avg', 'Slope', 'Intercept', 'hourly-velocity'])
        event_timeshifts = pd.DataFrame(offset_rows, columns=['Start', 'Stop', 'Pearson', 'Ratio', 'RMSE', 'RMSE_Artemis', 'RMSE_Omni', 'RMSE_Avg', 'Slope', 'Intercept'])

        if os.path.exists(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/'.format(artemis['Time'][0].strftime('%Y-%m-%d_%H-%M'), k))):
            event_metadata.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/metrics.csv'.format(artemis['Time'][0].strftime('%Y-%m-%d_%H-%M'), k)))
            event_timeshifts.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/timeshifts.csv'.format(artemis['Time'][0].strftime('%Y-%m-%d_%H-%M'), k)))

        else:
            os.makedirs(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/'.format(artemis['Time'][0].strftime('%Y-%m-%d_%H-%M'), k)))
            event_metadata.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/metrics.csv'.format(artemis['Time'][0].strftime('%Y-%m-%d_%H-%M'), k)))
            event_timeshifts.to_csv(os.path.join(workingDir, 'Solar-Wind-Reliability/output-data/hourly-correlations/{}/{}/timeshifts.csv'.format(artemis['Time'][0].strftime('%Y-%m-%d_%H-%M'), k)))

    print('Done.')


def main():
    projDir = '/Volumes/Research'
    artemisDirectory = os.path.join(projDir, 'Solar-Wind-Reliability/output-data/GSE/Artemis/')
    omniDirectory = os.path.join(projDir, 'Solar-Wind-Reliability/output-data/GSE/Omni/')

    omniFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(omniDirectory, x)), os.listdir(omniDirectory)))
    artemisFileList = sorted(filter(lambda x: os.path.isfile(os.path.join(artemisDirectory, x)), os.listdir(artemisDirectory)))

    file_pairs = [(os.path.join(artemisDirectory, artemis_file), os.path.join(omniDirectory, omni_file)) for artemis_file, omni_file in zip(artemisFileList, omniFileList) if not artemis_file.startswith('.') and not 'copy' in artemis_file]

    with ProcessPoolExecutor() as executor:
        executor.map(correlate, file_pairs, [projDir] * len(file_pairs))

if __name__ == "__main__":
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    print(f"Executed in {elapsed_time:.4f} seconds")

#-----------------------------------------------------------------------------------------------------------------------


'''
for nums, files in enumerate(omniFileList):
    print('{} - {}'.format(nums, files))
toCorrelate = input('Please enter the number of the file you wish to correlate, or type "all" to correlate the whole folder: ')


if toCorrelate == 'all':
    for l in range(len(omniFileList)):
        if not omniFileList[l].startswith('.') and not 'copy' in omniFileList[l]:
            print('Correlating {}...'.format(omniFileList[l]))
            artemisData = pd.read_csv(os.path.join(artemisDirectory, artemisFileList[l]), delimiter=',', header=0)
            omniData = pd.read_csv(os.path.join(omniDirectory, omniFileList[l]), delimiter=',', header=0)
            artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
            omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')

            correlate(artemisData, omniData, projDir)

elif int(toCorrelate) < len(omniFileList):
    print('Correlating {} and {}...'.format(omniFileList[int(toCorrelate)], artemisFileList[int(toCorrelate)]))
    artemisData = pd.read_csv(os.path.join(artemisDirectory, artemisFileList[int(toCorrelate)]), delimiter=',', header=0)
    omniData = pd.read_csv(os.path.join(omniDirectory, omniFileList[int(toCorrelate)]), delimiter=',', header=0)
    artemisData['Time'] = pd.to_datetime(artemisData['Time'], format='%Y-%m-%d %H:%M:%S')
    omniData['Time'] = pd.to_datetime(omniData['Time'], format='%Y-%m-%d %H:%M:%S')

    correlate(artemisData, omniData, projDir)

else:
    raise ValueError('Must be "any" or less than {}'.format(len(omniFileList)))
'''