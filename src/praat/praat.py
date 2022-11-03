
import os
import json
import subprocess


def callSexDetection(wav_path):
    praatScript = os.path.abspath("src/praat/getMeanF0.praat")
    if (os.path.isfile(praatScript)):
        praat = path2Praat()
        if (os.path.isfile(praat)):
            tmp = wav_path.split("/")
            wav_path = os.path.abspath(wav_path)
            wav_name = tmp[-1].split(".")[0]
            cmd = praat + " --run " + praatScript + " " + wav_path + " " + wav_name
            return subprocess.getoutput(cmd)
    return None


def callPowerDetection(wav_path, start, end):
    praatScript = os.path.abspath("src/praat/getPower.praat")
    if (os.path.isfile(praatScript)):
        praat = path2Praat()
        if (os.path.isfile(praat)):
            tmp = wav_path.split("/")
            wav_path = os.path.abspath(wav_path)
            wav_name = tmp[-1].split(".")[0]
            cmd = praat + " --run " + praatScript + " " + \
                wav_path + " " + wav_name + " " + start + " " + end
            return subprocess.getoutput(cmd)
    return None


def callMFCCPraatScript(pathToWav):
    ''' '''
    if (os.path.isfile(pathToWav)):
        splittedPath = pathToWav.split("/")
        fileName = splittedPath[len(splittedPath) - 1].replace(".wav", "")
        pathToWav = os.path.abspath(pathToWav)
        mfccPath = pathToWav.replace(".wav", ".MFCC")
        praatScript = os.path.abspath("src/praat/createMFCCFile.praat")
        if (os.path.isfile(praatScript)):
            praat = path2Praat()
            if (os.path.isfile(praat)):
                subprocess.run([praat, "--run", praatScript,
                                pathToWav, fileName, mfccPath])


def path2Praat():
    with open("src/config.json", "r") as pathToJson:
        content = pathToJson.read()
        obj = json.loads(content)

        return obj["praat"]
