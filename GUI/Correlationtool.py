import PySimpleGUI as sg
import numpy as np
import datetime as dt
import pandas as pd
import pyspedas
from pytplot import del_data, get_data, get_timespan, store_data, tplot_options, tplot_names, tplot, tplot_math

#---Functions-----------------------------------------------------------
def get_omni(start, stop, fixed):
    if fixed:
        start = start+dt.timedelta(minutes=30)

    trange = [start.strftime("%Y-%m-%d/%H:%M:%S"), stop.strftime("%Y-%m-%d/%H:%M:%S")] #Timeseries should be in the format [pd.Timestamp, pd.Timestamp]
    omni_import = pyspedas.omni.data(trange=trange, datatype='1min', level='hro2', time_clip=True)

    omni = {'Time': get_data('IMF')[0], 'BX_GSE': get_data('BX_GSE')[1], 'BY_GSE': get_data('BY_GSE')[1], 'BZ_GSE': get_data('BZ_GSE')[1], 'Vx': get_data('Vx')[1], 'Vy': get_data('Vy')[1], 'Vz': get_data('Vz')[1], 'proton_density': get_data('proton_density')[1], 'T': get_data('T')[1]}
    omni_data = pd.DataFrame(omni, columns=['Time', 'BX_GSE', 'BY_GSE', 'BZ_GSE', 'Vx', 'Vy', 'Vz', 'proton_density', 'T']).replace(to_replace=[999.990, 9999.99, 99999.9], value=np.nan)
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
    artemis_fgm_data = pd.DataFrame(fgm, columns=['Time', 'BX_GSE', 'BY_GSE', 'BZ_GSE'])
    artemis_fgm_data['Time'] = pd.to_datetime(artemis_fgm_data['Time'], unit='s')

    artemis_fgm_data = artemis_fgm_data.set_index('Time').resample('T').mean()
    #--------------------------------------------------------------------------------------------------------------------------------------

    #---ARTEMIS ESA data manipulation-------------------------------------------------------------------------------------------------------
    esa = {'Time': get_data('thb_peif_velocity_gse')[0], 'Vx': get_data('thb_peif_velocity_gse')[1][:,0], 'Vy': get_data('thb_peif_velocity_gse')[1][:,1], 'Vz': get_data('thb_peif_velocity_gse')[1][:,2], 'proton_density': get_data('thb_peif_density')[1], 'T': get_data('thb_peif_avgtemp')[1]}
    artemis_esa_data = pd.DataFrame(esa, columns=['Time', 'Vx', 'Vy', 'Vz', 'proton_density', 'T'])
    artemis_esa_data['Time'] = pd.to_datetime(artemis_esa_data['Time'], unit='s')

    artemis_esa_data = artemis_esa_data.set_index('Time').resample('T').mean().interpolate(method='linear')
    #--------------------------------------------------------------------------------------------------------------------------------------\

    return artemis_fgm_data, artemis_esa_data

def get_themis(start, stop, probe, fixed):
    if fixed:
        start = start+dt.timedelta(minutes=30)

    trange = [start.strftime("%Y-%m-%d/%H:%M:%S"), stop.strftime("%Y-%m-%d/%H:%M:%S")] #Timeseries should be in the format [pd.Timestamp, pd.Timestamp]
    themis_fgm_import = pyspedas.themis.fgm(trange=trange, probe=probe, time_clip=True, varnames='th'+probe+'_fgs_gse')
    themis_esa_import = pyspedas.themis.esa(trange=trange, probe=probe, time_clip=True, varnames=['th'+probe+'_peif_velocity_gse', 'th'+probe+'_peif_density', 'th'+probe+'_peif_avgtemp'])

    #---THEMIS FGM data manipulation-------------------------------------------------------------------------------------------------------
    fgm = {'Time': get_data('th'+probe+'_fgs_gse')[0], 'BX_GSE': get_data('th'+probe+'_fgs_gse')[1][:,0], 'BY_GSE': get_data('th'+probe+'_fgs_gse')[1][:,1], 'BZ_GSE': get_data('th'+probe+'_fgs_gse')[1][:,2]}
    themis_fgm_data = pd.DataFrame(fgm, columns=['Time', 'BX_GSE', 'BY_GSE', 'BZ_GSE'])
    themis_fgm_data['Time'] = pd.to_datetime(themis_fgm_data['Time'], unit='s')

    themis_fgm_data = themis_fgm_data.set_index('Time').resample('T').mean()
    #--------------------------------------------------------------------------------------------------------------------------------------

    #---THEMIS ESA data manipulation-------------------------------------------------------------------------------------------------------
    esa = {'Time': get_data('th'+probe+'_peif_velocity_gse')[0], 'Vx': get_data('th'+probe+'_peif_velocity_gse')[1][:,0], 'Vy': get_data('th'+probe+'_peif_velocity_gse')[1][:,1], 'Vz': get_data('th'+probe+'_peif_velocity_gse')[1][:,2], 'proton_density': get_data('th'+probe+'_peif_density')[1], 'T': get_data('th'+probe+'_peif_avgtemp')[1]}
    themis_esa_data = pd.DataFrame(esa, columns=['Time', 'Vx', 'Vy', 'Vz', 'proton_density', 'T'])
    themis_esa_data['Time'] = pd.to_datetime(themis_esa_data['Time'], unit='s')

    themis_esa_data = themis_esa_data.set_index('Time').resample('T').mean().interpolate(method='linear')
    #--------------------------------------------------------------------------------------------------------------------------------------

    return themis_fgm_data, themis_esa_data


def open_csv(path):
    event_string = []
    events = pd.read_csv(path, delimiter=',', header=0)
    events['time_start'] = pd.to_datetime(events['time_start'])
    events['time_stop'] = pd.to_datetime(events['time_stop'])
    for t in range(len(events['time_start'])):
        event_string.append([events['time_start'][t].strftime('%y-%m-%d/%H:%M:%S'), events['time_stop'][t].strftime('%y-%m-%d/%H:%M:%S')])

    return event_string

def load_data(satellite1, satellite2):
    i = 0
    if satellite1 == 'artemis':
        artemis_fgm, artemis_esa = get_artemis(events['time_start'][i], events['time_stop'][i], fixed=False)
        sat1 = pd.concat([artemis_fgm, artemis_esa], axis=1)

    elif satellite1 == 'themis' and satellite2 != 'themis':
        themis_fgm, themis_esa = get_themis(events['time_start'][i], events['time_stop'][i], probe=events['THEMIS'][i],
                                            fixed=False)
        sat1 = pd.concat([themis_fgm, themis_esa], axis=1)

    else:
        raise ValueError("String '" + satellite1 + "' is not one of ('artemis', 'themis')")

    if satellite2 == 'themis' and satellite1 != 'themis':
        themis_fgm, themis_esa = get_themis(events['time_start'][i], events['time_stop'][i], probe=events['THEMIS'][i],
                                            fixed=True)
        sat2 = pd.concat([themis_fgm, themis_esa], axis=1)
    elif satellite2 == 'omni':
        sat2 = get_omni(events['time_start'][i], events['time_stop'][i], fixed=True)

    return sat1, sat2,
#-----------------------------------------------------------------------

eventlist=[]
sg.theme("Default 1")

row1 = [[sg.Text("Load events (.csv)"), sg.In(size=(50, 1), enable_events=True), sg.FileBrowse(key="-CSV-"), sg.Button("Submit")],
        [sg.Text("Load ~/path/to/file.csv", key="-LOADED-")]]

col1 = [[sg.Text("Choose satellite 1:")],
        [sg.Text("Choose satellite 2:")]]

col2 = [[sg.Radio("ARTEMIS", "RADIO1", default=True, key="-ART-"), sg.Radio("THEMIS", "RADIO1", key="-THM1-"), sg.Radio("MMS", "RADIO1", key="-MMS1-")],
        [sg.Radio("OMNI", "RADIO2", default=True, key="-OMNI-"), sg.Radio("THEMIS", "RADIO2", key="-THM2-"), sg.Radio("MMS", "RADIO2", key="-MMS2-")]]

col3 = [[sg.Radio("Correlate all events", "RADIO3", disabled=True, key="-ALL-"), sg.Radio("Correlate single event", "RADIO3", key="-ONE-")],
        [sg.Combo(values=eventlist, default_value="Select...", size=(40, 1), enable_events=True, key="-EVENT-", readonly=True)]]

col4 = [[sg.Button("Get")]]

row2 = [[sg.Text("Options:"), sg.Button("Plot Event", key="-PE-", disabled=True), sg.Button("Correlate Events", key="-CE-", disabled=True), sg.Button("Show Data", key="-SD-", disabled=True), sg.Text("(Spawns new window)")]]


def main():
    layout = [[sg.Column(row1, element_justification='l')],
              [sg.Column(col1, element_justification='l'), sg.Column(col2, element_justification='l'),
               sg.VerticalSeparator(), sg.Column(col3, element_justification='l'), sg.Column(col4, element_justification='l')],
              [sg.HorizontalSeparator()],
              [sg.Column(row2, element_justification='l')]]

    window = sg.Window("Correlation Tool", layout, size=(700, 600))

    while True:
        event, values = window.read()

        if event == "Submit":
            e, s = open_csv(values["-CSV-"])
            eventlist = s
            window["-LOADED-"].update(value="Loaded " + values["-CSV-"])
            window["-EVENT-"].update(values=eventlist)
        if event == "Get":

            sat1 = values["RADIO1"]
            sat2 = values["RADIO2"]
            print(sat1, sat2, do_not_reroute_stdout=False)

            window["-PE-"].update(disabled=False)
            window["-CE-"].update(disabled=False)
            window["-SD-"].update(disabled=False)
        if event == "-SD-":
            sg.Print(e, do_not_reroute_stdout=False)

        if event == "OK" or event == sg.WIN_CLOSED:
            break
    window.close()

if __name__ == "__main__":
    main()