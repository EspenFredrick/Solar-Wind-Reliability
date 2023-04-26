import numpy as np
import datetime as dt
import pandas as pd
import pyspedas
from pytplot import get_data
from scipy.constants import physical_constants

#----------------------------------------------------------------------------------------------------------------------------
def get_omni(start, stop, fixed):
    if fixed:
        start = start+dt.timedelta(minutes=30)

    trange = [start.strftime("%Y-%m-%d/%H:%M:%S"), (stop-dt.timedelta(minutes=1)).strftime("%Y-%m-%d/%H:%M:%S")] #Timeseries should be in the format [pd.Timestamp, pd.Timestamp]
    omni_import = pyspedas.omni.data(trange=trange, datatype='1min', level='hro2', time_clip=True)

    omni = {'Time': get_data('IMF')[0], 'BX_GSE': get_data('BX_GSE')[1], 'BY_GSE': get_data('BY_GSE')[1], 'BZ_GSE': get_data('BZ_GSE')[1], 'Vx': get_data('Vx')[1], 'Vy': get_data('Vy')[1], 'Vz': get_data('Vz')[1], 'proton_density': get_data('proton_density')[1], 'T': get_data('T')[1]}
    omni_data = pd.DataFrame(omni, columns=['Time', 'BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']).replace(to_replace=[999.990, 9999.99, 99999.9, 9999999], value=np.nan)
    omni_data['Time'] = pd.to_datetime(omni_data['Time'], unit='s')

    omni_data = omni_data.set_index('Time').interpolate(method='linear')

    return omni_data

def get_artemis(start, stop, fixed):
    if fixed:
        start = start+dt.timedelta(minutes=30)

    trange = [start.strftime("%Y-%m-%d/%H:%M:%S"), stop.strftime("%Y-%m-%d/%H:%M:%S")] #Timeseries should be in the format [pd.Timestamp, pd.Timestamp]
    artemis_fgm_import = pyspedas.themis.fgm(trange=trange, probe='b', time_clip=True, varnames='thb_fgs_gse')
    artemis_esa_import = pyspedas.themis.esa(trange=trange, probe='b', time_clip=True, varnames=['thb_peif_velocity_gse', 'thb_peif_density', 'thb_peif_avgtemp'])

    #---ARTEMIS FGM data manipulation-------------------------------------------------------------------------------------------------------
    fgm = {'Time': get_data('thb_fgs_gse')[0], 'BX_GSE': get_data('thb_fgs_gse')[1][:,0], 'BY_GSE': get_data('thb_fgs_gse')[1][:,1], 'BZ_GSE': get_data('thb_fgs_gse')[1][:,2]}
    artemis_fgm_data = pd.DataFrame(fgm, columns=['Time', 'BX_GSE', 'BY_GSE', 'BZ_GSE']).replace(to_replace=[999.990, 9999.99, 99999.9], value=np.nan)
    artemis_fgm_data['Time'] = pd.to_datetime(artemis_fgm_data['Time'], unit='s')

    artemis_fgm_data = artemis_fgm_data.set_index('Time').resample('T').mean().interpolate(method='linear')
    #--------------------------------------------------------------------------------------------------------------------------------------

    #---ARTEMIS ESA data manipulation-------------------------------------------------------------------------------------------------------
    esa = {'Time': get_data('thb_peif_velocity_gse')[0], 'Vx': get_data('thb_peif_velocity_gse')[1][:,0], 'Vy': get_data('thb_peif_velocity_gse')[1][:,1], 'Vz': get_data('thb_peif_velocity_gse')[1][:,2], 'proton_density': get_data('thb_peif_density')[1], 'T': get_data('thb_peif_avgtemp')[1]}
    artemis_esa_data = pd.DataFrame(esa, columns=['Time', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']).replace(to_replace=[999.990, 9999.99, 99999.9], value=np.nan)
    artemis_esa_data['T'] = artemis_esa_data['T'] / physical_constants['Boltzmann constant in eV/K'][0]
    artemis_esa_data['Time'] = pd.to_datetime(artemis_esa_data['Time'], unit='s')

    artemis_esa_data = artemis_esa_data.set_index('Time').resample('T').mean().interpolate(method='linear')
    artemis_esa_data = artemis_esa_data.reindex(artemis_fgm_data.index)
    #---------------------------------------------------------------------------------------------------------------------------------------

    return artemis_fgm_data, artemis_esa_data

def get_themis(start, stop, probe, fixed):
    if fixed:
        start = start+dt.timedelta(minutes=30)

    trange = [start.strftime("%Y-%m-%d/%H:%M:%S"), stop.strftime("%Y-%m-%d/%H:%M:%S")] #Timeseries should be in the format [pd.Timestamp, pd.Timestamp]
    themis_fgm_import = pyspedas.themis.fgm(trange=trange, probe=probe, time_clip=True, varnames='th'+probe+'_fgs_gse')
    themis_esa_import = pyspedas.themis.esa(trange=trange, probe=probe, time_clip=True, varnames=['th'+probe+'_peif_velocity_gse', 'th'+probe+'_peif_density', 'th'+probe+'_peif_avgtemp'])

    #---THEMIS FGM data manipulation-------------------------------------------------------------------------------------------------------
    fgm = {'Time': get_data('th'+probe+'_fgs_gse')[0], 'BX_GSE': get_data('th'+probe+'_fgs_gse')[1][:,0], 'BY_GSE': get_data('th'+probe+'_fgs_gse')[1][:,1], 'BZ_GSE': get_data('th'+probe+'_fgs_gse')[1][:,2]}
    themis_fgm_data = pd.DataFrame(fgm, columns=['Time', 'BX_GSE', 'BY_GSE', 'BZ_GSE']).replace(to_replace=[999.990, 9999.99, 99999.9], value=np.nan)
    themis_fgm_data['Time'] = pd.to_datetime(themis_fgm_data['Time'], unit='s')

    themis_fgm_data = themis_fgm_data.set_index('Time').resample('T').mean().interpolate(method='linear')
    #--------------------------------------------------------------------------------------------------------------------------------------

    #---THEMIS ESA data manipulation-------------------------------------------------------------------------------------------------------
    esa = {'Time': get_data('th'+probe+'_peif_velocity_gse')[0], 'Vx': get_data('th'+probe+'_peif_velocity_gse')[1][:,0], 'Vy': get_data('th'+probe+'_peif_velocity_gse')[1][:,1], 'Vz': get_data('th'+probe+'_peif_velocity_gse')[1][:,2], 'proton_density': get_data('th'+probe+'_peif_density')[1], 'T': get_data('th'+probe+'_peif_avgtemp')[1]}
    themis_esa_data = pd.DataFrame(esa, columns=['Time', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']).replace(to_replace=[999.990, 9999.99, 99999.9], value=np.nan)
    themis_esa_data['T'] = themis_esa_data['T'] / physical_constants['Boltzmann constant in eV/K'][0]
    themis_esa_data['Time'] = pd.to_datetime(themis_esa_data['Time'], unit='s')

    themis_esa_data = themis_esa_data.set_index('Time').resample('T').mean().interpolate(method='linear')
    themis_esa_data = themis_esa_data.reindex(themis_fgm_data.index)
    #--------------------------------------------------------------------------------------------------------------------------------------

    return themis_fgm_data, themis_esa_data

#---------------------------------------------------------------------------------------------------------------------------