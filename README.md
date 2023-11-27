# Solar Wind Reliability - Determining the reliability of OMNI data to predict solar wind conditions at Earth
### This repository contains the scripts and data products produced by this research project.
___
### Contact Info:
**Name:** Espen Fredrick *(Lead graduate student)*  
**Email:** espen.fredrick@uta.edu

**Name:** Rushikesh Patil *(Undergraduate researcher)*  
**Email:** rushikesh.patil@mavs.uta.edu

**Name:** James Truett *(Undergraduate researcher)*  
**Email:** jtd4566@mavs.uta.edu
___

### Table of Contents:
- README.md - *This file.*
- [Scripts](./scripts) - *Python (.py) and Jupyter (.ipynb) scripts used to calculate correlation coefficients, process data, make plots, import data, etc.*
- [Output Data](./output-data) - *Contains the generated metadata files.*
- [Event List](./eventlist) - *Contains the list of events used in analysis.*

Solar-Wind-Reliability/
├── scripts/
│   ├── data-importing/
│   │   ├── DataImporter.py
│   │   ├── GetSatellitesGSE.py
│   │   └── GetSatellitesGSM.py
│   ├── data-analysis/
│   │   ├── Correlator-Parallel.py
│   │   ├── IdentifyStructure.py
│   │   ├── CSVCombiner.py
│   │   └── MetricAverager.py
│   └── plotting/
│       ├── Plotter-Parallel.py
│       ├── Scatterplots.py
│       ├── DistPlotter.py
│       ├── HistPlotter.py
│       └── Animator.ipynb
├── output-data
├── gui-programs
├── eventlist
└── readme.md

