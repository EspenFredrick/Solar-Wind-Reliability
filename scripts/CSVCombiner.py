#----------------------------------------------------------------------------------------------------------------------------
#
#
#       $$$$$$   /$$$$$$  /$$    /$$  /$$$$$$                          /$$       /$$
#     /$$__  $$ /$$__  $$| $$   | $$ /$$__  $$                        | $$      |__/
#    | $$  \__/| $$  \__/| $$   | $$| $$  \__/  /$$$$$$  /$$$$$$/$$$$ | $$$$$$$  /$$ /$$$$$$$   /$$$$$$   /$$$$$$
#    | $$      |  $$$$$$ |  $$ / $$/| $$       /$$__  $$| $$_  $$_  $$| $$__  $$| $$| $$__  $$ /$$__  $$ /$$__  $$
#    | $$       \____  $$ \  $$ $$/ | $$      | $$  \ $$| $$ \ $$ \ $$| $$  \ $$| $$| $$  \ $$| $$$$$$$$| $$  \__/
#    | $$    $$ /$$  \ $$  \  $$$/  | $$    $$| $$  | $$| $$ | $$ | $$| $$  | $$| $$| $$  | $$| $$_____/| $$
#    |  $$$$$$/|  $$$$$$/   \  $/   |  $$$$$$/|  $$$$$$/| $$ | $$ | $$| $$$$$$$/| $$| $$  | $$|  $$$$$$$| $$
#     \______/  \______/     \_/     \______/  \______/ |__/ |__/ |__/|_______/ |__/|__/  |__/ \_______/|__/
#
#                                            -- By Espen Fredrick --
#                                                   04/25/2023
#
# Simple script to import all the data files in a given folder and merge them together.
#----------------------------------------------------------------------------------------------------------------------------

import pandas as pd
import os

files = [f for f in os.listdir("../metadata/output-data") if os.path.isfile(os.path.join("../metadata/output-data", f)) and f.endswith(".csv")]

frame = []
for fileName in files:
    print(os.path.join("../metadata/output-data", fileName))
    frm = pd.read_csv(os.path.join("../metadata/output-data", fileName), delimiter=',', header=0, index_col=0)
    frame.append(frm)
df = pd.concat(frame)
df.to_csv('../metadata/MergedEvents.csv')