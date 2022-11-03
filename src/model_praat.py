
import os
import subprocess

import config


def parseTextGrid(textGrid: str):
    """Create segment information from textgrid file
    @called by: model

    Args:
        textGrid (str): file path to a TextGrid file

    Returns:
        [(str, float, float)]: list of segments of phoneme label, start time, and end time
    """
    times = []
    counter = 0
    secondCounter = 0
    foundWortTier = False
    tempStart = 0
    tempEnd = 0
    if os.path.isfile(textGrid):
        with open(textGrid, "r", encoding="utf-8") as openFile:
            try:
                lines = openFile.readlines()
            except UnicodeDecodeError:
                with open(textGrid, "r", encoding="utf-16-be") as oF:
                    lines = oF.readlines()
            for line in lines:
                if "name = \"MAU\"" in line:
                    foundWortTier = True
                elif "name = " in line:
                    foundWortTier = False
                if foundWortTier:
                    if "xmin =" in line:
                        tempStart = line.split("=")[1].strip()
                        secondCounter += 1
                    elif "xmax =" in line:
                        tempEnd = line.split("=")[1].strip()
                        secondCounter += 1
                    elif "text = " in line:
                        if "text = \"\"" in line or "<p:>" in line:
                            secondCounter = 0
                        else:
                            secondCounter += 1
                            phoneme = line.split("=")[1].strip("\" \n")
                    else:
                        secondCounter = 0
                    if (secondCounter == 3):
                        times.append(
                            (phoneme, float(tempStart), float(tempEnd)))
                        counter += 1
                        secondCounter = 0
    return times


def parseMFCCFile(mfccFilePath: str, calc_config: config.Calc_Config):
    """Create mfcc data from MFCC file
    @called by: model

    Args:
        mfccFilePath (str): path to a MFCC file
        calc_config (config.Calc_Config): holding calculation config data

    Returns:
        dict(float: [[float]]): time2frames
    """
    mfccVectors = dict()
    timeStep = 0
    startTime = 0
    foundFrame = False
    currentTime = 0
    if os.path.isfile(mfccFilePath):
        with open(mfccFilePath, 'r') as openFile:
            try:
                lines = openFile.readlines()
            except UnicodeDecodeError:
                with open(mfccFilePath, 'r', encoding='utf-16-be') as oF:
                    lines = oF.readlines()
            for line in lines:
                if "dx = " in line:
                    timeStep = float(line.replace("dx =", "").strip())
                elif "x1 = " in line:
                    startTime = float(line.replace("x1 =", "").strip())
                elif "frame [" in line:
                    temp = line.replace(
                        "frame [", "").replace("]:", "").strip()
                    if temp != '':
                        temp = int(temp)
                        if temp != 0:
                            foundFrame = True
                            currentTime = (temp * timeStep) + startTime
                            mfccVectors[currentTime] = []
                if foundFrame:
                    if calc_config.with_c0:
                        if "c0 = " in line:
                            c0 = float(line.replace("c0 =", "").strip())
                            mfccVectors[currentTime].append(c0)

                    if "c [" in line and "] =" in line:
                        if int(line.split("c [")[1].split("] =")[0]) > calc_config.n_mfccs:
                            continue
                        cX = float(line.split("=")[1].strip())
                        mfccVectors[currentTime].append(cX)
    return mfccVectors


def callMFCCPraatScript(pathToWav: str, calc_config: config.Calc_Config, path2Praat: str,
                        praat_script="src/praat/createMFCCFile.praat"):
    """Create a MFCC file through Praat
    @called by: model

    Args:
        pathToWav (str): path to praat file
        calc_config (config.Calc_Config): holding calculation config data
        path2Praat (str): path to Praat executable
        praat_script (str, optional): path to the praat script. Defaults to "src/praat/createMFCCFile.praat".

    Returns:
        config.ErrorMessages: error message indicating an error in the creation process
    """
    if (os.path.isfile(pathToWav)):
        splittedPath = pathToWav.split("/")
        fileName = splittedPath[len(splittedPath) - 1].replace(".wav", "")
        pathToWav = os.path.abspath(pathToWav)
        mfccPath = pathToWav.replace(".wav", ".MFCC")
        if os.path.isfile(mfccPath):
            return config.ErrorMessages.MFCC_FILES_EXIST
        else:
            praatScript = os.path.abspath(praat_script)
            if (os.path.isfile(praatScript)):
                praat = path2Praat
                if (os.path.isfile(praat)):
                    subprocess.run([praat, "--run", praatScript,
                                    pathToWav, fileName, mfccPath,
                                    str(calc_config.number_of_coef), str(
                                        calc_config.window_length),
                                    str(calc_config.time_step), str(
                                        calc_config.first_filter_freq),
                                    str(calc_config.distance_filters), str(calc_config.max_freq)])
                    return config.ErrorMessages.NO_ERROR
                else:
                    return config.ErrorMessages.MISSING_PRAAT_PATH


def merge_praatMFCCs_TG(frames, tg_data):
    """Merge mfccs and textgrid information
    @called by: model

    Args:
        frames ( dict(float, [[float]]) ): time2frames
        tg_data ([(str, float, float)]): list of segments of label, start time, and end time

    Returns:
        dict(str, [[float]]): phoneme2mfccs 
    """
    mfccs_by_phonem = dict()

    for time_point, mfccs in frames.items():
        for (label, start, end) in tg_data:
            if time_point >= start and time_point <= end:
                # found correct segment
                if not label in mfccs_by_phonem.keys():
                    mfccs_by_phonem[label] = []
                mfccs_by_phonem[label].append(mfccs)
                break

    return mfccs_by_phonem
