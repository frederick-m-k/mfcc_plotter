

import numpy as np


def normalize_mfccs_remove_phonem(frames2norm, additional_frames):
    """Normalize mfccs. Remove phoneme information
    @called by: model

    Args:
        frames2norm ([[float]]): the frames of the speaker and phoneme to normalize
        additional_frames ([[float]]): the frames of the other speaker and the same phoneme

    Returns:
        [[float]]: return the normalized frames of the speaker and phoneme
    """
    mean = _custom_mean(frames2norm + additional_frames)
    std = _custom_std(frames2norm + additional_frames)

    return list(np.divide(np.subtract(frames2norm, mean), std))


def normalize_mfccs_remove_speaker(mfccs):
    """Normalize mfccs. Remove speaker information
    @called by: model

    Args:
        mfccs ( dict(str: [[float]]) ): mfccs to normalize

    Returns:
        dict(str: [[float]]): altered/normalized mfccs
    """
    all_mfccs = []
    for frames in mfccs.values():
        [all_mfccs.append(frame) for frame in frames]
    mean_mfcc = _custom_mean(all_mfccs)
    sd_mfcc = _custom_std(all_mfccs)
    # [[frame1], [frame2], ...]]
    for phonem, frames in mfccs.items():
        for i in range(len(frames)):
            mfccs[phonem][i] = list(np.divide(np.subtract(
                mfccs[phonem][i], mean_mfcc), sd_mfcc))
    return mfccs


def _custom_std(double_array, n_mfccs=13):
    """Get the standard deviation of each mfcc dimension in an n_mfccs-dimensional list
    @called by: internal

    Args:
        double_array ([[float]]): list of frames
        n_mfccs (int, optional): Defaults to 13.

    Returns:
        [[float]]: standard deviations of each mfcc dimension
    """
    result = []
    for i in range(n_mfccs):
        one_mfcc = []
        for j in range(len(double_array)):
            one_mfcc.append(double_array[j][i])
        result.append(np.std(one_mfcc))
    return result


def _custom_mean(double_array, n_mfccs=13):
    """Get the means of each mfcc dimension in an n_mfccs-dimensional list
    @called by: internal

    Args:
        double_array ([[float]]): list of frames
        n_mfccs (int, optional): Defaults to 13.

    Returns:
        [[float]]: standard deviations of each mfcc dimension
    """
    result = []
    for i in range(n_mfccs):  # 0, 1, 2
        summe = 0
        counter = 0
        for j in range(len(double_array)):
            summe += double_array[j][i]
            counter += 1
        result.append(summe / counter)
    return result
