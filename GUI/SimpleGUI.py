import PySimpleGUI as sg
import csv
import os.path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime as dt


#---Functions-----------------------------------------------------------
def open_csv(file):

    #keys = ['Correlation Coef. (Bx)', 'Correlation Coef. (By)', 'Correlation Coef. (Bz)', 'Time Offset Bx (sec.)', 'Time Offset By (sec.)', 'Time Offset Bz (sec.)', 'Average Bx (nT)', 'Average By (nT)', 'Average Bz (nT)']
    #params = dict((k, []) for k in keys)

    with open(file) as data:
        rows = csv.reader(data)
        headers = next(rows)
        params = dict((k, []) for k in headers)

        for r in rows:
            for i, j in enumerate(params):
                if ':' in str(r[i]):
                    params[j].append(dt.strptime(r[i], '%Y-%m-%d %H:%M:%S'))
                else:
                    params[j].append(np.float64(r[i]))

    return params

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def delete_fig_agg(fig_agg):
    fig_agg.get_tk_widget().forget()
    plt.close('all')

def linear(x, m ,b):
    return (m*x) + b

#-----------------------------------------------------------------------
list1 = []

sg.theme("Default 1")

row1 = [[sg.Text("Choose .csv"), sg.In(size=(50, 1), enable_events=True), sg.FileBrowse(key="-CSV-"), sg.Button("Submit")],
        [sg.Text("Load ~/path/to/file.csv", key="-LOADED-")]]

col1 = [[sg.Text("X-axis variable:")],
        [sg.Text("Y-axis variable:")],
        [sg.Text("Plot Style:")]]

col2 = [[sg.Combo(values=list1, default_value='Select...', size=(30, 1),  enable_events=True, key="-XSELECT-")],
        [sg.Combo(values=list1, default_value='Select...', size=(30, 1),  enable_events=True, key="-YSELECT-")],
        [sg.Radio("Scatter", "RADIO1", default=True, key="-SCAT-"), sg.Radio("Line", "RADIO1", key="-LINE-")]]

col3 = [[sg.Text("Plot title:")],
        [sg.Text("X-axis label:")],
        [sg.Text("Y-axis label:")]]

col4 = [[sg.In(size=(30, 1), enable_events=True, default_text="Title", key="-TITLE-")],
        [sg.In(size=(30, 1), enable_events=True, default_text="X-axis", key="-XLABEL-")],
        [sg.In(size=(30, 1), enable_events=True, default_text="Y-axis", key="-YLABEL-")]]

plotbtn = [[sg.Button("Create Plot")]]
#sg.In(size=(50, 1), enable_events=True), sg.FolderBrowse(key="-SAVE-"), sg.Button("Save figure")

out = [[sg.Canvas(key='-CANVAS-')]]

layout = [[sg.Column(row1, element_justification='l')],
          [sg.Column(col1, element_justification='l'), sg.Column(col2, element_justification='l'), sg.Column(col3, element_justification='l'), sg.Column(col4, element_justification='l')],
          [plotbtn],
          [out]]

window = sg.Window("Plot Tool", layout, size=(900,700))

fig_canvas_agg = None

while True:
    event, values = window.read()
    if event == "Submit":
        l = open_csv(values["-CSV-"])
        list1 = []
        for i in l.keys():
            list1.append(str(i))

        window.find_element("-LOADED-").update(value="Loaded "+values["-CSV-"])
        window.find_element("-XSELECT-").update(values=list1)
        window.find_element("-YSELECT-").update(values=list1)

    if event == "Create Plot":
        if fig_canvas_agg is not None:
            delete_fig_agg(fig_canvas_agg)

        xaxis = l[values["-XSELECT-"]]
        yaxis = l[values["-YSELECT-"]]

        fig = plt.figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)

        if values["-SCAT-"] == True:
            ax.scatter(xaxis, yaxis, alpha=0.5, color='black')

        if values["-LINE-"] == True:
            ax.plot(xaxis, yaxis, alpha=0.5, color='black')

        ax.set_title(values["-TITLE-"])
        ax.set_xlabel(values["-XLABEL-"])
        ax.set_ylabel(values["-YLABEL-"])
        ax.tick_params(axis='both', direction='in')

        fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
        window.find_element("-CANVAS-").update()

    elif event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()
