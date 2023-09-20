#----------------------------------------------------------------------------------------------------------------------------
#
#
#   /$$$$$$$              /$$               /$$$$$$                                               /$$
#   | $$__  $$            | $$              |_  $$_/                                              | $$
#   | $$  \ $$  /$$$$$$  /$$$$$$    /$$$$$$   | $$   /$$$$$$/$$$$   /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$
#   | $$  | $$ |____  $$|_  $$_/   |____  $$  | $$  | $$_  $$_  $$ /$$__  $$ /$$__  $$ /$$__  $$|_  $$_/   /$$__  $$ /$$__  $$
#   | $$  | $$  /$$$$$$$  | $$      /$$$$$$$  | $$  | $$ \ $$ \ $$| $$  \ $$| $$  \ $$| $$  \__/  | $$    | $$$$$$$$| $$  \__/
#   | $$  | $$ /$$__  $$  | $$ /$$ /$$__  $$  | $$  | $$ | $$ | $$| $$  | $$| $$  | $$| $$        | $$ /$$| $$_____/| $$
#   | $$$$$$$/|  $$$$$$$  |  $$$$/|  $$$$$$$ /$$$$$$| $$ | $$ | $$| $$$$$$$/|  $$$$$$/| $$        |  $$$$/|  $$$$$$$| $$
#   |_______/  \_______/   \___/   \_______/|______/|__/ |__/ |__/| $$____/  \______/ |__/         \___/   \_______/|__/
#                                                                 | $$
#                                                                 | $$
#                                                                 |__/
#
#                                            -- By Espen Fredrick --
#                                                   03/03/2023
#
# Data importing script that parses PySpedas and downloads/interpolates data to a one-minute cadence. Options to plot the
# output are also included.
#----------------------------------------------------------------------------------------------------------------------------

import pandas as pd
from getSatellitesGSE import *

satellite1 = input('Please enter the first satellite to study (either "artemis" or "themis"): ')
satellite2 = input('Please enter the second satellite to study (either "omni" or "themis): ')
path = input('Please enter the path to the list of events: ')

events = pd.read_csv(path, delimiter=',', header=0)
events['time_start'] = pd.to_datetime(events['time_start'])
events['time_stop'] = pd.to_datetime(events['time_stop'])

for event in range(len(events['time_start'])):

    if satellite1 == 'artemis':
        artemis_fgm, artemis_esa = get_artemis(events['time_start'][event], events['time_stop'][event], fixed=False)
        sat1 = pd.concat([artemis_fgm, artemis_esa], axis=1).interpolate(method='linear').fillna(method='bfill')
        sat1_name = 'Artemis'

    elif satellite1 == 'themis' and satellite2 != 'themis':
        themis_fgm, themis_esa = get_themis(events['time_start'][event], events['time_stop'][event], probe=events['THEMIS'][event], fixed=False)
        sat1 = pd.concat([themis_fgm, themis_esa], axis=1).interpolate(method='linear').fillna(method='bfill')
        sat1_name = 'Themis'

    else:
        raise ValueError('String "{}" is not one of ("artemis", "themis")'.format(satellite1))

    if satellite2 == 'themis' and satellite1 != 'themis':
        themis_fgm, themis_esa = get_themis(events['time_start'][event], events['time_stop'][event], probe=events['THEMIS'][event], fixed=True)
        sat2 = pd.concat([themis_fgm, themis_esa], axis=1).interpolate(method='linear').fillna(method='bfill')
        sat2_name = 'Themis'
    elif satellite2 == 'omni':
        sat2 = get_omni(events['time_start'][event], events['time_stop'][event], fixed=True)
        sat2_name = 'Omni'
    else:
        raise ValueError('String "{}" is not one of ("omni", "themis")'.format(satellite2))


    sat1.reset_index(inplace=True)
    sat2.reset_index(inplace=True)

    sat1.to_csv('../output-data/GSE-with-xpos/'+sat1_name+'/'+sat1_name+'_'+events['time_start'][event].strftime("%Y-%m-%d_%H-%M")+'.csv')
    sat2.to_csv('../output-data/GSE-with-xpos/'+sat2_name+'/'+sat2_name+'_'+events['time_start'][event].strftime("%Y-%m-%d_%H-%M")+'.csv')