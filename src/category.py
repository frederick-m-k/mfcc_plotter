
import numpy as np

class Category:
    """Class to hold information on a recording-phoneme combi with their mfccs and color information
    @called by: view
    """

    def __init__(self, recording: str, phoneme: str, mfccs: dict):
        """Initiate an object to hold graphical information and mfccs of one recording-phoneme combi
        @called by: view

        Args:
            recording (str): recording name
            phoneme (str)
            mfccs (dict(str, [[float]]) ): phoneme2frames
        """
        self.speaker = recording
        self.phonem = phoneme
        self.mfccs = mfccs
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
        self._init()

    def _init(self):
        """Initiate statistical information, i.e. quantiles, max, min, and median, of the mfccs
        @called by: internal
        """
        self.values = list(self._calc_quant_mfccs(self.mfccs, 0.25))
        for quant in list(self._calc_quant_mfccs(self.mfccs, 0.75)):
            self.values.append(quant)
        self.max = np.max(self.values)
        self.min = np.min(self.values)
        self.medians = self._calc_medians_mfccs(self.mfccs)

    def _calc_medians_mfccs(self, all_mfccs: dict):
        """Calculate the median of each dimension
        @called by: internal

        Args:
            all_mfccs (dict(str, [[float]]) )

        Returns:
            [float]: one median per mfcc dimension
        """
        median_mfccs = []

        for i in range(13):
            one_coefficent = []
            for mfccs in all_mfccs:
                one_coefficent.append(mfccs[i])
            median_mfccs.append(np.median(one_coefficent))

        return median_mfccs

    def _calc_quant_mfccs(self, all_mfccs: dict, q: float):
        """Calculate a quantile of each mfcc dimension
        @called by: internal

        Args:
            all_mfccs (dict(str, [[float]]) )
            q (float): which quantile, e.g. 0.25 or 0.75

        Returns:
            [float]: one quantile value per dimension
        """
        return np.quantile(all_mfccs, q, axis=0)


####
# here are the class functions
####

    def calc_quant_mfccs(all_mfccs: dict, q: float):
        """Class function. Calculate a quantile of each mfcc dimension
        @called by: DeathStar

        Args:
            all_mfccs (dict(str, [[float]]) )
            q (float): which quantile, e.g. 0.25 or 0.75

        Returns:
            [float]: one quantile value per dimension
        """
        return np.quantile(all_mfccs, q, axis=0)

    def calc_medians_mfccs(all_mfccs: dict):
        """Class function. Calculate the median of each dimension
        @called by: DeathStar

        Args:
            all_mfccs (dict(str, [[float]]) )

        Returns:
            [float]: one median per mfcc dimension
        """
        median_mfccs = []

        for i in range(13):
            one_coefficent = []
            for mfccs in all_mfccs:
                one_coefficent.append(mfccs[i])
            median_mfccs.append(np.median(one_coefficent))

        return median_mfccs