import PySimpleGUI as sg
import numpy as np
import datetime as dt
import pandas as pd
from correlator import correlate

eventlist=[]
sg.theme("Default 1")

row1 = [[sg.Text("Load Satellite 1 (.csv)"), sg.In(size=(50, 1), enable_events=True), sg.FileBrowse(key="sat1")]]

row2 = [[sg.Text("Load Satellite 2 (.csv)"), sg.In(size=(50, 1), enable_events=True), sg.FileBrowse(key="sat2"), sg.Button("Submit")]]


col2 = [[sg.Radio("ARTEMIS", "RADIO1", default=True, key="-ART-"), sg.Radio("THEMIS", "RADIO1", key="-THM1-"), sg.Radio("MMS", "RADIO1", key="-MMS1-")],
        [sg.Radio("OMNI", "RADIO2", default=True, key="-OMNI-"), sg.Radio("THEMIS", "RADIO2", key="-THM2-"), sg.Radio("MMS", "RADIO2", key="-MMS2-")]]

col3 = [[sg.Radio("Correlate all events", "RADIO3", disabled=True, key="-ALL-"), sg.Radio("Correlate single event", "RADIO3", key="-ONE-")],
        [sg.Combo(values=eventlist, default_value="Select...", size=(40, 1), enable_events=True, key="-EVENT-", readonly=True)]]

col4 = [[sg.Button("Get")]]

row4 = [[sg.Text("Options:"), sg.Button("Plot Event", key="-PE-", disabled=True), sg.Button("Correlate Events", key="-CE-", disabled=True), sg.Button("Show Data", key="-SD-", disabled=True), sg.Text("(Spawns new window)")]]


def main():
    layout = [[sg.Column(row1, element_justification='l')],
              [sg.Column(row2, element_justification='l')],
              [sg.Column(col2, element_justification='l'),
               sg.VerticalSeparator(), sg.Column(col3, element_justification='l'), sg.Column(col4, element_justification='l')],
              [sg.HorizontalSeparator()],
              [sg.Column(row4, element_justification='l')]]

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