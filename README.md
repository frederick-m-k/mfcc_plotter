# MFCC-Plotter
This repository contains the project MFCC-Plotter.


## Overview
*MFCC-Plotter* is a graphical and interactive method to compare cepstal data, specifically MFCCs.
The MFCCs are displayed in 13 dimensions in a polar-box-plot like structure.
![Screenshot of the main menu of the MFCC plotter comparing the phoneme /f/ from two different input sources](src/imgs/main_menu_plotter.png)
It allows the comparison of two plots next to each other.


## Technical background
Used packages are found in the `requirements.txt` file.

### Old repository
In an older version, the MFCC-Plotter used to be part of a bigger repo with several projects: https://gitlab.lrz.de/ru95job/speakerrecognitionproject.git

### Versions
| version | comment |
| - | - |
| v0.5.0 | intial version on this repo |
| v0.5.1 | code got cleaned |
| v0.6.0 | dropdown menus for selection options |
| v0.7.0 | added parsing option for _annot.json files |
| v0.8.0 | added actual research results in the resources/ dir |
| v0.8.1 | found and removed error with the information menu |


## Research results
The directory `resources/` contains one sub directory with some research results.

### Research on emotional speech
In the directory `resources/wasep_public_results/` are three PDF-files located. They compare, of two speakers of 318 recordings in total, compare either
- different phonemes for one emotion-contrast or
- the same phoneme in five emotion-contrasts.
These results are mainly an extension for a paper for the research conference ESSV 2023 (https://www.phonetik.uni-muenchen.de/ESSV2023/essv2023en.html).
Once the paper is published, it will be linked here as well.