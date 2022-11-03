# MFCC-Plotter
This repository contains the project MFCC-Plotter.

## Overview
*MFCC-Plotter* is a graphical and interactive method to compare cepstal data, specifically MFCCs.
The MFCCs are displayed in 13 dimensions in a polar-box-plot like structure.
**Screenshot here**
It allows the comparison of two plots next to each other.

## Current work
- export of MFCCs and Plots
    - needed for it -> more space & separate possibility to export for both death stars
    - solution
        - make mfcc-calc and mfcc-norm options into smaller dropdown menu
            - currently working on this
        - toolbar above new dropdown menus for every death star
    - additional thought -> info menu in middle of toolbar (where craftyy man go for theirb afterwork beer)
- clean code and make view and model as classes
    - missing cleanup: view
    - model and view not classes yet


### Gedanken zum Treffen
- nächster Milestone: Treffen mit Flow und Christoph
    - thematische Vorbereitung auf folgende Themen
        - Vanessa: Analyse von Sex-Appeal & Evaluation von Sprachsynthese-Systemen
        - Frederick: Prognosetool & akustischer Fingerabdruck & Bedeutung einzelner Dimensionen
- zweiter Milestone: Einreichen von Papern bei Konferenzen
    - ESSV: Fokus auf "Tool, um cepstrale Forschung zu boosten"
    - ICPhs (vielleicht): "Lots of /i/s in the MFCC-Plotter" / "How was it to use the MFCC-Plotter" -> erste Anwendung
    - Interspeech: "Lots of /i/s in the MFCC-Plotter" / "How was it to use the MFCC-Plotter" -> erste Anwendung
- nötige Schritte für Software
    2. Export von Plots und MFCCs
    3. mit deltas beschäftigen
    4. Import von MFCCs
    5. hatching only when overlapping rectangles
    6. resolve errors
    7. dev on Windows
    8. Bereitstellen als git repository

### Offene Punkte
- Anwendungsbereiche
    - Analyse von mehreren Lauten, in denen F1, F2 gleich bleibt und F0 verändert wird -> was verändert sich in cepstralen Daten?
    - same for gleiche F0 und Veränderung von F1, F2
    - Anzeige einer typischen Verteilung im Hintergrund -> z.B. regionale Varietät
    - Analyse von Knarrstimme
    - Analyse von Stille
    - Forensik
    - Analyse von Störgeräuschen
    - Prognosetool für Sprach- oder Sprechererkennung        -> Frederick
    - Finden des akustischen Fingerabdrucks eines Sprechers  -> Frederick
    - was bedeuten die einzelnen Dimensionen?                -> Frederick
    - Analyse von Sex-Appeal                                 -> Vanessa
        - Ali Niebuhr aus Kopenhagen
    - Evaluation von Sprachsynthese-System                   -> Vanessa
- als Website
- Tool in der Lehre testen
    - Wintersemester ist P6 zu Spracherkennung und Sprachsynthese
- Input von James Kirby
    - Verbindung von bekannter Darstellung von z.B. Formanten mit neuer Darstellung der MFCCs
        - auch erste Idee für eine Forschungsfrage
        - Recherche nötig, was bereits dazu geforscht wurde
- Mailing-Liste :()
- features
    - graphics
        - rethink and redesign graphics
            - maybe have a talk with Fiona Draxler, Kago or someone else from Media Informatics
        - grey gradient in merge-mode instead of rectangles. Or plot hatching only when real overlapping present
        - "runde" Boxplots
        - nice button design
        - issue with display of rec names when 7+ recordings loaded into one death star
    - backend functionality
        - create logger
    - frontend functionality
        - Export von MFCCs bzw. von nur den 50-Quantil-Daten
        - export plots in png or pdf format
        - Import von eigenen MFCCs
        - Anpassung der Parameter der MFCC-Berechnung
        - one sonagramm of the currently displayed phoneme -> available through button
        - Darstellung von Vokalen und Konsonanten
        - pie menus für die Phonemauswahl
        - openSmile and kaldi as new calc option
        - Unterschiedliche Normalisierungsarten (nicht nur CMVN sondern auch CMN oder Anderes)
        - provide interface for R and browser
        - possiblity to add whiskers to death star
        - play function
        - disco on play -> two possibilities
            - all coefficients of each frame light up sequentially
            - all mfccs of the phoneme are plotted sequentially
        - button to project selection to other death star
        - "Entfernung" zwischen zwei Phonemen
    - Angabe des Grades der Überlappung von zwei Phonemen oder Dimensionen
    - x flat joke result: show answer after packing/place without update (triggerd by cursor keyboard input)
- errors and bugs
    - dev for windows
        - window does not fit screensize on windows
        - white/off-white colours on windows
    - statistic menus still to see when merge button is pressed (and single stat menus were displayed)
    - when anything changes in any death star -> update everything
    - some weird issues with the axes in the statistics menu -> seems to happen after selecting different phonemes in merged mode and the switching to unmerged
    - move the label MFCC X


## Fragen an Christoph
- Bezahlung von Konferenzen (bei nicht Studies)
- Feedback von Flo
    - er betreut nicht
    - er kein Experte
    - Absprache mit Christoph passiert?
- Feedback von einigen: Forschungsprojekt und Promotion eher unrealistisch
- Ist Forschungsprojekt oder Promotion (für zwei) für dich realistisch?
    - welches Forschungsprojekt?
    - welche Richtung?
    - Betreuung?
    - nur Softwareentwicklung
- sind rein konzeptionelle Arbeiten verbreitet?
- Wer ist Experte?
- was genau ist in einem Forschungsprojekt enthalten?
- zeitlicher Horizont
- Anträge für Forschungsprojekte
    - reichen thematische Orientierungen?
    - sind konkrete Forschungsfragen nötig?


### Feedback von Harrington und Draxler
- Promotion rund um Plotter geht nicht, sondern sollte Mittel zum Zweck sein
- Zukunft ist nicht in München, da Fokus zu sehr bei Harrington's Thema
- Vorschlag von Christoph: Flo, Christoph, Vanessa, FK in einem 4er-Treffen
    - dafür vorbereiten: was genau heißt es, MFCCs in Forensik oder bei Sex-Appeal zu verwenden


### Technical background
Found in the `src/mfcc_display/` directory. Will be separated into a new repository before going into production.
Developed with python and tkinter.
Used packages are found in the `requirements.txt` file.

### Old repository
In an older version, the MFCC-Plotter used to be part of a bigger repo with several projects: https://gitlab.lrz.de/ru95job/speakerrecognitionproject.git

### Versions
| version | comment |
| - | - |
| v0.5.0 | intial version on this repo |
| | |