

import config
from config import logging as logging
import model_librosa
import model_praat
import normalize_mfccs

import json
import os

###### global variables
global all_mfccs

global praat_path
global default_file_path

global calc_config
global conf_config


def init_model():
    """Initialize all model-wide important variables.
    Also load user config data from the config.json file
    @called by: Controller
    """
    logging.debug("Initiating the model")
    global praat_path
    global default_file_path
    global calc_config
    global conf_config
    global all_mfccs
    all_mfccs = dict()
    if os.path.isfile("src/config.json"):
        logging.debug("Reading configuration from config.json")
        config_data = json.load(open("src/config.json", 'r', encoding="utf-8"))
        praat_path = config_data["praat"]
        default_file_path = config_data["default_file_path"]
    else:
        logging.info("Creating a new config.json file")
        open("src/config.json", 'w', encoding="utf-8").close()
        praat_path = ""
        default_file_path = "/"

    logging.info("praat path from user config is " + str(praat_path))
    logging.info("default file path from user config is " +
                 str(default_file_path))

    calc_config = config.Calc_Config()
    conf_config = config.Config()


def set_praat_path(new_path):
    """Set model-wide variable praat_path
    @called by: view

    Args:
        new_path (str): new path praat to set
    """
    global praat_path
    praat_path = new_path


def set_def_file_path(new_path):
    """Set model-wide variable which holds the last used file path
    @called by: view

    Args:
        new_path (str): new file path to set
    """
    global default_file_path
    if os.path.exists(new_path):
        default_file_path = new_path
    else:
        default_file_path = '/'


def check_file_input(input):
    """Check, if the files, provided by the user, are correct
    @called by: DeathStar

    Args:
        input ((str)): by user selected files

    Returns:
        config.ErrorMessage: enum which holds information about the exact error
    """
    wav_c = 0
    tg_c = 0
    for file_name in input:
        if file_name.endswith(".wav"):
            wav_c += 1
        elif file_name.endswith(".TextGrid"):
            tg_c += 1

    if conf_config.n_filepairs != None:
        if wav_c != conf_config.n_filepairs:
            return config.ErrorMessages.NO_WAV
        elif tg_c != conf_config.n_filepairs:
            return config.ErrorMessages.NO_TG
    else:
        if wav_c != tg_c:
            return config.ErrorMessages.NON_MATCHING_FILE_AMOUNT

    short_names = []
    for file_name in input:
        split = file_name.split("/")
        short_names.append(split[len(split) - 1].split(".")[0])
    for name in short_names:
        if short_names.count(name) != 2:
            return config.ErrorMessages.NON_MATCHING_FILE_NAMES

    return config.ErrorMessages.NO_ERROR


def get_rec_names(input):
    """Get the names of the recordings, i.e. the path of the filename before the .wav
    @called by: DeathStar

    Args:
        input ( (str) ): tuple of filenames

    Returns:
        [str]: list of all distinct names of the recordings
    """
    all_rec_names = set()
    for inp in input:
        short_inp = inp.split("/")
        all_rec_names.add(short_inp[len(short_inp) - 1].split(".")[0])
    return list(all_rec_names)


def create_mfccs(all_filenames):
    """Create and gather all mfccs of all calculation options
    @called by: DeathStar

    Args:
        all_filenames ([str]): all by the user selected filenames

    Returns:
        [(str, config.ErrorMessages)]: all error messages accummulated through the MFCC creation process
    """
    praat_errors = []

    rec_names = get_rec_names(all_filenames)
    for rec_name in rec_names:
        _create_librosa_mfccs(
            [fn for fn in all_filenames if rec_name in fn], rec_name)
        tmp_errors = _create_praat_mfccs(
            [fn for fn in all_filenames if rec_name in fn], rec_name)
        [praat_errors.append(tmp) for tmp in tmp_errors]
    return praat_errors


def _create_librosa_mfccs(filenames, rec_name):
    """Calculate the mfccs through the librosa library and append them to the mfcc dict-structure
    @called by: internal

    Args:
        filenames ([str]): list of filenames provided
        rec_name (str): the rec_name, which is in all the filenames
    """
    if not rec_name in all_mfccs.keys():
        all_mfccs[rec_name] = dict()

    wav, tg = sorted(filenames, reverse=True)
    raw_mfccs = model_librosa.run_librosa(wav, calc_config)
    without_c0 = model_librosa.remove_c0(raw_mfccs)
    edited_mfccs = model_librosa.ndArrayToList(without_c0)
    tg_data = model_praat.parseTextGrid(tg)
    wav_length = model_librosa.get_duration(wav)

    _add_new_mfccs(
        model_librosa.merge_librosaMFCCs_TG(edited_mfccs, tg_data, wav_length),
        rec_name,
        "librosa"
    )


def _create_praat_mfccs(filenames, rec_name):
    """Calculate the mfccs through Praat and append them to the mfcc dict-structure
    @called by: internal

    Args:
        filenames ([str]): list of filenames provided
        rec_name (str): the rec_name, which is in all the filenames

    Returns:
        [(str, config.ErrorMessages)]: list of tuple of (wav filename, errorMessage)
    """
    if not rec_name in all_mfccs.keys():
        all_mfccs[rec_name] = dict()
    all_mfccs[rec_name]["praat"] = dict()

    new_mfcc_files = []

    wav, tg = sorted(filenames, reverse=True)
    err_message = model_praat.callMFCCPraatScript(wav, calc_config, praat_path)
    new_mfcc_files.append((wav, err_message))

    mfcc_frames = model_praat.parseMFCCFile(
        wav.replace(".wav", ".MFCC"), calc_config)
    tg_data = model_praat.parseTextGrid(tg)

    _add_new_mfccs(
        model_praat.merge_praatMFCCs_TG(mfcc_frames, tg_data),
        rec_name,
        "praat"
    )

    return new_mfcc_files


def _add_new_mfccs(new_mfccs, rec_name, calc_method):
    """Add newly calculated mfccs to the already existing all_mfccs dict-structure
    @called by: internal

    Args:
        new_mfccs ( dict(str, [[float]]) ): mfccs to add to the existing all_mfccs structure
        rec_name (str): name of the recording
        calc_method (str): name of the current calculation option
    """
    if calc_method not in all_mfccs[rec_name].keys():
        all_mfccs[rec_name][calc_method] = dict()

    for pho, frames in new_mfccs.items():
        if not pho in all_mfccs[rec_name][calc_method].keys():
            all_mfccs[rec_name][calc_method][pho] = []
        for frame in frames:
            all_mfccs[rec_name][calc_method][pho].append(frame)


def get_recName2phoneme(rec_names):
    """
    @called by: DeathStar

    Args:
        rec_names ([str]): all distinct names of the recordings

    Returns:
        dict(str, [str]): name of the recording mapped to their phonemes
    """
    speaker2phoneme = dict()
    for name in rec_names:
        speaker2phoneme[name] = list(all_mfccs[name]["librosa"].keys())
    return speaker2phoneme


def get_all_mfccs(rec_names):
    """Return a merged list of all mfccs of all the provided recording names
    @called by: DeathStar

    Args:
        rec_names ([str]): distinct names of all recordings

    Returns:
        dict(str, [[float]]), dict(str, [[float]]): all mfccs calculated with praat, all mfccs calulcated with librosa
    """
    mfccs = {
        "librosa": dict(),
        "praat": dict(),
    }
    for name in rec_names:
        for calc in mfccs.keys():
            for pho, frames in all_mfccs[name][calc].items():
                if not pho in mfccs[calc].keys():
                    mfccs[calc][pho] = []
                for frame in frames:
                    mfccs[calc][pho].append(frame)

    return mfccs["librosa"], mfccs["praat"]


def norm_mfccs_rem_speaker(mfccs):
    """Normalize mfccs. Remove speaker information
    @called by: DeathStar

    Args:
        mfccs ( dict(str: [[]]) ): mfccs to normalize

    Returns:
        dict(str: dict(str: [[]])): rec2phoneme2frames
    """
    return normalize_mfccs.normalize_mfccs_remove_speaker(mfccs)


def norm_mfccs_rem_phonem(utt_ids, calc_option, phoneme2norm):
    """Normalize mfccs. Remove phoneme information
    @called by: DeathStar

    Args:
        utt_ids ([str]): the ids of the utterance to normalize
        calc_option (str)
        phoneme2norm (str)

    Returns:
        dict(str, [[float]]): phoneme2frames
    """
    frames2norm = []
    normalizerFrames = []
    for cur_utt, val in all_mfccs.items():
        if phoneme2norm in val[calc_option].keys():
            if cur_utt in utt_ids:
                [frames2norm.append(frame)
                 for frame in val[calc_option][phoneme2norm]]
            else:
                [normalizerFrames.append(frame)
                 for frame in val[calc_option][phoneme2norm]]

    normed_frames = normalize_mfccs.normalize_mfccs_remove_phonem(
        frames2norm, normalizerFrames)
    ret_dict = dict()
    ret_dict[phoneme2norm] = normed_frames
    return ret_dict


def save_config_file():
    """Save the (potentially) updated config data in the config.json file
    @called by: view
    """
    to_save = {
        "praat": praat_path,
        "default_file_path": default_file_path
    }
    json.dump(to_save, open("src/config.json", 'w', encoding="utf-8"))
