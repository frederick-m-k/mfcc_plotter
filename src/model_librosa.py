
import librosa
import numpy as np
import config


def run_librosa(dataPath: str, calc_config: config.Calc_Config):
    """Create mfccs with librosa. Automatically fill in config calculation option
    @called by: model

    Args:
        dataPath (str): path to wav file

    Returns:
        [[float]]: list of mfccs. shape(n_mfccs, amount of frames)
    """
    y, sr = librosa.load(dataPath)
    x = librosa.feature.mfcc(
        y=y, sr=sr, n_mfcc=calc_config.n_mfccs+1, hop_length=calc_config.hop_length)
    return x


def remove_c0(raw_librosa_mfccs):
    """The DCT which is done in librosa seems to return the c0 as well.
    Therefore, we have to remove it because we do not want to plot it
    @called by: model

    Args:
        raw_librosa_mfccs ([[float]]): list of lists of mfccs, grouped by dimension (not by frame)

    Returns:
        [[float]]: the input just without c0
    """
    return raw_librosa_mfccs[1:]


def ndArrayToList(ndarray):
    """Transpose librosa mfccs (shaped like (n_mfccs, amount of frames)) into shape (amount of frames, n_mfccs) 
    @called by: model

    Args:
        ndarray ([[float]]): default librosa mfccs

    Returns:
        [[float]]: transposed mfccs
    """
    listStructure = []
    for array in ndarray:
        listStructure.append(np.ndarray.tolist(array))

    result = []
    allMFCCS = []
    for frame in range(0, len(listStructure[0])):
        for mfcc in range(0, len(listStructure)):
            allMFCCS.append(listStructure[mfcc][frame])
        result.append(allMFCCS)
        allMFCCS = []
    return result


def get_duration(wav: str):
    """Get duration calculated by librosa
    @called by: model

    Args:
        wav (str): path to wav file

    Returns:
        float: duration
    """
    return librosa.get_duration(filename=wav)


def merge_librosaMFCCs_TG(frames, tg_data, wav_length: float):
    """TODO rename for annot.json and maybe replace
    Map textgrid data to mfcc frames
    @called by: model

    Args:
        frames ([[float]]): mfccs in shape (amount of frames, n_mfccs)
        tg_data ( [(str, float, float)] ): TextGrid data
        wav_length (float): duration of the wav file

    Returns:
        dict(str, [[float]]): phoneme2frames
    """
    mfccs_by_phonem = dict()

    distance = wav_length / len(frames)
    counter = 0
    for frame in frames:
        time_point = counter * distance

        for (label, start, end) in tg_data:
            if time_point >= start and time_point <= end:

                if not label in mfccs_by_phonem.keys():
                    mfccs_by_phonem[label] = []
                mfccs_by_phonem[label].append(frame)
                break

        counter += 1
    return mfccs_by_phonem
