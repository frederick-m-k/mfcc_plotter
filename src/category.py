
import numpy as np


class Category:

    def __init__(self, speaker, phonem, mfccs, first):  # constructor
        self.speaker = speaker
        self.phonem = phonem
        self.mfccs = mfccs
        self.first = first
        self.values = []
        self.min = 0
        self.max = 0
        self.medians = []
        self.main_color = ""
        self.edgecolor = ""
        self.facecolor = ""
        self.median_color = ""
        self.alpha = 0
        self.hatch = ""
        self.all_graphics = []
        self.init()

    def init(self):
        self.values = list(self.calc_quant_mfccs(self.mfccs, 0.25))
        for quant in list(self.calc_quant_mfccs(self.mfccs, 0.75)):
            self.values.append(quant)
        self.max = np.max(self.values)
        self.min = np.min(self.values)
        self.medians = self.calc_medians_mfccs(self.mfccs)

    # , main_color, edgecolor, facecolor, median_color, alpha, hatch):
    def set_color(self, colorCoding):
        ''' main_color, edgecolor, facecolor, median_color, alpha, hatch '''
        self.main_color = colorCoding[0]
        self.edgecolor = colorCoding[1]
        self.facecolor = colorCoding[2]
        self.median_color = colorCoding[3]
        self.alpha = colorCoding[4]
        self.hatch = colorCoding[5]

    def add_graphic(self, graphic):
        self.all_graphics.append(graphic)

    def clear_graphics(self):
        self.all_graphics.clear()

    def calc_medians_mfccs(self, all_mfccs):
        ''' param all_mfccs -> double array of all mfccs of one speaker of one phoneme '''
        median_mfccs = []

        for i in range(13):
            one_coefficent = []
            for mfccs in all_mfccs:
                one_coefficent.append(mfccs[i])
            median_mfccs.append(np.median(one_coefficent))

        return median_mfccs

    def calc_quant_mfccs(self, all_mfccs, q):
        return np.quantile(all_mfccs, q, axis=0)

    def get_first(self):
        return self.first


####
# here are the class functions
####

    def calc_quant_mfccs(all_mfccs, q):
        return np.quantile(all_mfccs, q, axis=0)

    def calc_medians_mfccs(all_mfccs):
        ''' param all_mfccs -> double array of all mfccs of one speaker of one phoneme '''
        median_mfccs = []

        for i in range(13):
            one_coefficent = []
            for mfccs in all_mfccs:
                one_coefficent.append(mfccs[i])
            median_mfccs.append(np.median(one_coefficent))

        return median_mfccs

    def calc_mean_mfccs(all_mfccs):
        mean_mfccs = []

        for i in range(13):
            one_coefficent = []
            for mfccs in all_mfccs:
                one_coefficent.append(mfccs[i])
            mean_mfccs.append(np.mean(one_coefficent))

        return mean_mfccs
