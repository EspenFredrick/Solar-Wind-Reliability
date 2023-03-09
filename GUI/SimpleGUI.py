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
        [sg.Text("Plot Style:")],
        [sg.Text("Plot size:")]]

col2 = [[sg.Combo(values=list1, default_value='Select...', size=(30, 1),  enable_events=True, key="-XSELECT-")],
        [sg.Combo(values=list1, default_value='Select...', size=(30, 1),  enable_events=True, key="-YSELECT-")],
        [sg.Radio("Scatter", "RADIO1", default=True, key="-SCAT-"), sg.Radio("Line", "RADIO1", key="-LINE-")],
        [sg.Text("X:"), sg.In(size=(4, 1), key="-XSIZE-", default_text='7'), sg.Text("Y:"), sg.In(size=(4, 1), key="-YSIZE-", default_text='3')]]

col3 = [[sg.Text("Plot title:")],
        [sg.Text("X-axis label:")],
        [sg.Text("Y-axis label:")],
        [sg.Text("Axis min/max:")]]

col4 = [[sg.In(size=(35, 1), enable_events=True, default_text="Title", key="-TITLE-")],
        [sg.In(size=(35, 1), enable_events=True, default_text="X-axis", key="-XLABEL-")],
        [sg.In(size=(35, 1), enable_events=True, default_text="Y-axis", key="-YLABEL-")],
        [sg.Text("Y:"), sg.In(size=(4, 1), key="-YMIN-"), sg.In(size=(4, 1), key="-YMAX-"), sg.Text("X:"), sg.In(size=(4, 1), key="-XMIN-"), sg.In(size=(4, 1), key="-XMAX-")]]


col5 = [[sg.Text("Point size:")],
        [sg.Text("Color:")],
        [sg.Text("Alpha:")],
        [sg.Text("Line/pt style:")]]

col6 = [[sg.Combo(values=[1,2,3,4,5,6,7,8,9,10], size=(8,1), key="-PTSIZE-", default_value=10)],
        [sg.InputCombo(values=['C0', 'C1', 'C2', 'C3', 'r', 'g', 'b', 'k'], size=(8,1), key="-COLOR-", default_value='C0')],
        [sg.Combo(values=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], size=(8,1), key="-ALPHA-", default_value=0.5)],
        [sg.Combo(values = [], size=(8, 1), key="-STYLE-")]]

row2 = [[sg.Text("Options:"), sg.Button("Create Plot"), sg.Button("Linear Fit")]]


#sg.In(size=(50, 1), enable_events=True), sg.FolderBrowse(key="-SAVE-"), sg.Button("Save figure")

out = [[sg.Canvas(key='-CANVAS-')]]

layout = [[sg.Column(row1, element_justification='l')],
          [sg.Column(col1, element_justification='l'), sg.Column(col2, element_justification='l'), sg.Column(col3, element_justification='l'), sg.Column(col4, element_justification='l'), sg.Column(col5, element_justification='l'), sg.Column(col6, element_justification='l')],
          [sg.HSeparator()],
          [row2],
          [out]]

window = sg.Window("Plot Tool", layout, size=(900, 700))

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

    if values["-SCAT-"] == True:
        window["-STYLE-"].update(values=['o', 's', 'D', '+'])

        if event == "Create Plot":
            if fig_canvas_agg is not None:
                delete_fig_agg(fig_canvas_agg)

            xaxis = l[values["-XSELECT-"]]
            yaxis = l[values["-YSELECT-"]]

            fig = plt.figure(figsize=(int(values["-XSIZE-"]), int(values["-YSIZE-"])), dpi=200)
            ax = fig.add_subplot(111)

            ax.scatter(xaxis, yaxis, alpha=values["-ALPHA-"], color=values["-COLOR-"], s=int(values["-PTSIZE-"]))
            ax.set_title(values["-TITLE-"])
            ax.set_xlabel(values["-XLABEL-"])
            ax.set_ylabel(values["-YLABEL-"])
            ax.tick_params(axis='both', direction='in')
            if values["-YMIN-"] and values["-YMAX-"] is not None:
                ax.set_ylim([float(values["-YMIN-"]), float(values["-YMAX-"])])
            if values["-XMIN-"] and values["-XMAX-"] is not None:
                ax.set_xlim([float(values["-XMIN-"]), float(values["-XMAX-"])])
            plt.tight_layout()
            plt.show()

            fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
            window.find_element("-CANVAS-").update()


    if values["-LINE-"] == True:
        window["-STYLE-"].update(values=['-', ':'])

        if event == "Create Plot":
            if fig_canvas_agg is not None:
                delete_fig_agg(fig_canvas_agg)

            xaxis = l[values["-XSELECT-"]]
            yaxis = l[values["-YSELECT-"]]

            fig = plt.figure(figsize=(8, 5), dpi=100)
            ax = fig.add_subplot(111)

            ax.plot(xaxis, yaxis, alpha=int(values["-ALPHA"]), color=values["-COLOR-"], linestyle=values["-PTSIZE-"])
            ax.set_title(values["-TITLE-"])
            ax.set_xlabel(values["-XLABEL-"])
            ax.set_ylabel(values["-YLABEL-"])
            ax.tick_params(axis='both', direction='in')
            plt.tight_layout()
            plt.show()

            fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
            window.find_element("-CANVAS-").update()

    elif event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()
