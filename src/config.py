
import enum
import numpy as np

import logging
logging.basicConfig(level=logging.WARNING)


class Norm(enum.Enum):
    """Enum to hold config strings for normalization options
    """
    REM_SPEAKER = "remove speaker"
    REM_PHONEME = "remove phoneme"
    NO_NORM = "no normalization"


class ErrorMessages(enum.Enum):
    """Enum to hold some error messages
    """
    SAME_PHONEME = "You selected the same phoneme of one speaker twice.\nThis is not implemented yet.\nPlease change it to two different phonemes."
    MISSING_PRAAT_PATH = "You did not enter a valid path to your praat installation. \nPlease add the path in the information menu."
    MFCC_FILES_EXIST = "A .MFCC file already exists. No new .MFCC file has been created."
    NO_ERROR = "Die Zwiebeln zwiebeln: everythings alright"

    NO_WAV = "Max .wav-file amount exceeded"
    NO_TG = "Max .TextGrid-file amount exceeded"
    NO_ANNOT_JSON = "Max _annot.json-file amount exceeded"
    NON_MATCHING_FILE_AMOUNT = "The number of provided wavs and TextGrids do not match"
    NON_MATCHING_FILE_NAMES = "The provided file pairs (TextGrid and wav) should all match in their filename"


class Calc(enum.Enum):
    """Enum to hold config strings for calculation options
    """
    PRAAT = "praat"
    LIBROSA = "librosa"


class ColorCoding(enum.Enum):
    """Enum to hold default color information
    """
    # deprecated
    CAT1 = ("#00000019", "white", "blue", "#10efb7", 0.2, "+")
    CAT2 = ("#00000019", "#fe923a", "none", "red", 0.2, "+")
    CAT3 = ("#00000019", "white", "blue", "#10efb7", 0.2, "o")
    CAT4 = ("white", "#fe923a", "none", "red", 0.2, "o")
    ####

    # xxxx, edgecolor, facecolor, median, opacity, hatching, boxplot, mergedYesNo, position
    # edgecolor is main color for COMB1, facecolor is main color for COMB2
    COMB1 = ("#00000019", "#09cbf6", "none",
             "blue", 0.9, "/", "#09cbf6", False, "left")
    COMB2 = ("#00000019", "white", "purple", "red",
             0.9, "/", "purple", False, "right")
    MERG = ("#00000019", "purple", "none", "pink",
            0.9, "/", "purple", True, "middle")


class Config():
    """Class to hold default global variables
    """

    def __init__(self):
        self.n_filepairs = None

        self.n_mfccs = 13
        self.angles = np.linspace(
            0, 2*np.pi, num=self.n_mfccs, endpoint=False).tolist()
        self.angles += self.angles[:1]

        self.labels = ["MFCC "+str(i) for i in range(1, self.n_mfccs + 1)]

        self.app_name = "MFCC-Plotter"

        self.font_family = "Helvetica"  # "American Typewriter"
        self.font_size = 14
        self.heading_size = 25
        self.brand_size = 50

        self.treeview_font = "Menlo"

        self.start_prompt_text = "Welcome to our app " + self.app_name + \
            ".\nIn this app, you can visualize and compare different MFCCs with each other.\nIn the following, you have to select two different (wav, TextGrid) pairs of files. From those, you have to select two phonemes each.\nThose four phonemes will be graphically displayed.\nYou may modify the source of the MFCCs (e.g. Praat or librosa) and the normalization options.\n\n\nIf you have any feedback, trouble or suggestions for improvement, feel free to write us via Frederick.Kukla@campus.lmu.de and Vanessa.Reichel@campus.lmu.de\nAll the best,\nFrederick and Vanessa"  # Die zwiebeligen Zwei"


class Calc_Config():
    """Class to hold default global configuration variables
    """

    def __init__(self):
        self.n_mfccs = 13

        # praat
        self.with_c0 = False
        self.number_of_coef = 13
        self.window_length = 0.015
        self.time_step = 0.01
        self.first_filter_freq = 100
        self.distance_filters = 100
        self.max_freq = 0

        # librosa
        self.hop_length = 128
