
import math
import sys
import tkinter as tk
from tkinter import font, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

import config
from config import logging as logging
from deathStar import DeathStar
from custom_label import CustomLabel

import model

global root
global button_choose_file

global main_screen_width, main_screen_height

global info_im
global info_frame

global stars

conf = config.Config()
calc_config = config.Calc_Config()

tree2selected = dict()
selected_per_Frame = dict()

tree_labels = []

all_graphs = dict()
set_phonemes = dict()


def init_view():
    """Initiate all view-wide variables in the view
    @called by: controller
    """
    logging.debug("Initiating the view")
    global main_screen_width, main_screen_height
    global root
    global info_im
    root = tk.Tk()
    root.title(conf.app_name)

    main_screen_width = root.winfo_screenwidth()
    screen_width = int(main_screen_width - 0.1*main_screen_width)
    main_screen_height = root.winfo_screenheight()
    screen_height = int(main_screen_height - 0.1*main_screen_height)
    logging.debug("complete screen width is " + str(main_screen_width))
    logging.debug("complete screen height is " + str(main_screen_height))

    # first offset (to the right) does not work as intended on macOS
    root.geometry("{}x{}+{}+{}".format(screen_width,
                                       screen_height, int(0.05*main_screen_width), int(0.05*main_screen_height)))

    # font stuff
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family=conf.treeview_font, size=conf.font_size)

    default_font = font.nametofont("TkHeadingFont")
    default_font.configure(family=conf.font_family, size=conf.font_size)

    im = Image.open("src/imgs/information-button.png").resize((25, 25))
    info_im = ImageTk.PhotoImage(im)

    _init_start_screen()

    _init_information_screen()


def _init_start_screen():
    """Initialize a start screen with some background information
    @called by: internal
    """
    start_frame = tk.Frame(root)

    start_frame.place(anchor="center", relx=.5, rely=.5)

    start_prompt = tk.Label(start_frame, text=conf.start_prompt_text, font=(
        conf.font_family, conf.font_size))
    start_button = tk.Button(start_frame, text="Start the app", font=(conf.font_family, conf.font_size),
                             command=lambda: _switch_toDoubleDisplay(start_frame))

    start_prompt.pack(side="top")
    start_button.pack(side="top")


def _switch_toDoubleDisplay(frame: tk.Frame):
    """Show the two-DeathStar-display
    @called by: internal

    Args:
        frame (tk.Frame): frame to add the DeathStars to
    """
    global stars
    stars = []
    [ch.destroy() for ch in frame.winfo_children()]
    one_size = math.floor(main_screen_width / 240)
    left_star = DeathStar(frame, one_size, conf, config.ColorCoding.COMB1,
                          main_screen_width, main_screen_height, root)
    left_star.pack(side="left", padx=5)
    left_star.currently_seen = True
    stars.append(left_star)

    right_star = DeathStar(
        frame, one_size, conf, config.ColorCoding.COMB2, main_screen_width, main_screen_height, root)
    right_star.pack(side="right", padx=5)
    right_star.currently_seen = True
    stars.append(right_star)

    merged_star = DeathStar(
        frame, one_size, conf, config.ColorCoding.MERG, main_screen_width, main_screen_height, root)
    stars.append(merged_star)

    merge_button = tk.Button(frame, text="Merge",
                             command=lambda: _toggle_merge(merge_button, left_star, right_star, merged_star))
    merge_button.place(anchor="center", relx=.5, rely=.25)

    lab = tk.Label(frame, image=info_im)
    lab.place(anchor="center", relx=0.98, rely=.25)
    lab.bind("<Button-1>", lambda event: _show_information_screen(event))


def get_range_of_stars():
    """Get the minimal and maximal values of all mfccs in all stars
    @called by: DeathStar

    Returns:
        [float]: [x_bottom, x_top]
    """
    def get_range_of_merged(min_max):
        if len(star.left_mfccs) <= 0 or len(star.right_mfccs) <= 0:
            return 0
        if min_max == "min":
            return min(
                min([frame[star.current_coef] for frame in star.left_mfccs]),
                min([frame[star.current_coef] for frame in star.right_mfccs])
            )
        elif min_max == "max":
            return max(
                max([frame[star.current_coef] for frame in star.left_mfccs]),
                max([frame[star.current_coef] for frame in star.right_mfccs])
            )

    bottom = sys.maxsize
    top = 1 - sys.maxsize

    for star in stars:
        bottom = min(bottom,
                     bottom
                     if star.current_coef == -1
                     else min([frame[star.current_coef]
                               for frame in star.current_mfccs])
                     if len(star.current_mfccs) > 0
                     else get_range_of_merged("min"))

        top = max(top,
                  top
                  if star.current_coef == -1
                  else max([frame[star.current_coef]
                            for frame in star.current_mfccs])
                  if len(star.current_mfccs) > 0
                  else get_range_of_merged("max"))

    return [bottom-(0.05*abs(bottom)), top+(0.05*abs(top))]


def reload_other_statistics(star2not_reload: DeathStar):
    """Reload the statistics display of all DeathStars (except for one which is given as parameter)
    @called by: DeathStar

    Args:
        star2not_reload (DeathStar)
    """
    for star in stars:
        if star == star2not_reload:
            continue

        star.reload_statistics()


def _toggle_merge(button: tk.Button, left_star: DeathStar, right_star: DeathStar, merged_star: DeathStar):
    """Merge or unmerge the two DeathStars
    @called by: internal

    Args:
        button (tk.Button): to check if merged or not merged
        left_star (DeathStar)
        right_star (DeathStar)
        merged_star (DeathStar)
    """
    cur_text = button.cget("text")
    if cur_text == "Merge":
        if left_star.got_data and right_star.got_data:
            button.config(text="Unmerge")
            left_star.hide_star()
            left_star.currently_seen = False
            right_star.hide_star()
            right_star.currently_seen = False
            merged_star.place(anchor="center", relx=.5, rely=.65)
            merged_star.currently_seen = True
            merged_star.give_data(left_star.current_mfccs,
                                  right_star.current_mfccs)
    elif cur_text == "Unmerge":
        if left_star.got_data and right_star.got_data:
            merged_star.place_forget()
            merged_star.currently_seen = False
            button.config(text="Merge")
            left_star.show_star()
            left_star.currently_seen = True
            right_star.show_star()
            right_star.currently_seen = True
    root.update()

def on_option_change(event, stringVar: tk.StringVar, star: DeathStar):
    label = stringVar.get()
    phoneme = True
    for calc in config.Calc:
        if label == calc.value:
            star.calculation_option = label
            phoneme = False
    for norm in config.Norm:
        if label == norm.value:
            star.norm_option = label
            phoneme = False
    if phoneme:
        star.selected_phoneme = label
        if stars[0].check_phoneme(star.selected_phoneme) and stars[1].check_phoneme(star.selected_phoneme):
            star.add_norm_remPhoneme()
        else:
            star.remove_norm_remPhoneme()
    star.update_mfccs()
    if star.rect_id == None:
        star.show_mfccs()

    if stars[0].rect_id != None:  # this means, the two stars are merged
        stars[2].give_data(stars[0].current_mfccs, stars[1].current_mfccs)


def _init_information_screen():
    """Doing nothing right now... TODO: check if necessary
    @called by: internal
    """
    pass


def _show_information_screen():
    """Init and show information screen
    @called by: internal
    """
    global info_frame
    width = main_screen_width - 0.1*main_screen_width
    canvas_width = width - 0.05 * width
    main_height = main_screen_height - 0.1*main_screen_height
    info_frame = tk.Frame(root, background="white",
                          highlightbackground="grey", highlightthickness=4, width=width, height=main_height - 0.1*main_height)

    close_button = tk.Button(info_frame, text="Close",
                             command=_hide_information_screen)
    close_button.pack(side="bottom")

    info_praat = CustomLabel(info_frame, justify="center", text="""Currently used Praat path.
    On Unix like systems, you can find the path with \"where praat\" if you have Praat installed.""")
    # On Windows, ...""")
    info_praat.pack(side="top")

    input_praat = tk.Text(info_frame, height=1,
                          width=len(model.praat_path)+10, pady=3)
    input_praat.insert(tk.INSERT, model.praat_path)
    input_praat.focus_set()
    input_praat.pack(side="top")

    praat_path_button = tk.Button(info_frame, text="Set Praat path",
                                  command=lambda: _set_praat_path(input_praat, close_button))
    praat_path_button.pack(side="top", pady=5)

    canvas = tk.Canvas(info_frame, width=canvas_width, height=10, bg="white")
    canvas.create_line(0.05*canvas_width, 5,
                       canvas_width - 0.05*canvas_width, 5)
    canvas.pack(side="top")

    info_plots = CustomLabel(
        info_frame, justify="center", text="""The MFCCs are displayed as Boxplots.
        The colored box are the values between the 0.25 and 0.75 quantile.
        The lighter colored line is the median.
        The whiskers and outliers are dropped.""")
    info_plots.pack(side="top")

    canvas = tk.Canvas(info_frame, width=canvas_width, height=10, bg="white")
    canvas.create_line(0.05*canvas_width, 5,
                       canvas_width - 0.05*canvas_width, 5)
    canvas.pack(side="top")

    info_calc = CustomLabel(
        info_frame, justify="center", text="""MFCCs in Praat were calculated with the method \"To MFCC\" with the following parameters:
        Number of coefficients = """ + str(calc_config.number_of_coef) + """
        Window length (s) = """ + str(calc_config.window_length) + """
        Time step (s) = """ + str(calc_config.time_step) + """
        First filter frequency (mel) = """ + str(calc_config.first_filter_freq) + """
        Distance between filters (mel) = """ + str(calc_config.distance_filters) + """
        Maximum frequency (mel) = """ + str(calc_config.max_freq) + """

        MFCCs with librosa (v. 0.8.0) were calculated with the method librosa.feature.mfcc with the following parameters:
        Sampling rate (sr) = corresponding wav file
        n_mfcc = """ + str(calc_config.number_of_coef) + """
        hop_length = """ + str(calc_config.hop_length) + """
        the other parameters were not modified by their default""")
    info_calc.pack(side="top")

    canvas = tk.Canvas(info_frame, width=canvas_width, height=10, bg="white")
    canvas.create_line(0.05*canvas_width, 5,
                       canvas_width - 0.05*canvas_width, 5)
    canvas.pack(side="top")

    info_norm = CustomLabel(
        info_frame, justify="center", text="""calculated with CMVN (Cepstral Mean and Variance Normalization)
        remove speaker = always possible
            take mean and standard deviation of all phonemes of one speaker/utterance and
            subtract the mean and divide by the st dev for each frame of the same speaker/utterance

        remove phoneme = only possible when both speaker/utterances have the same selected phoneme
            take mean and standard deviation of all frames of the selected phoneme of both speakers/utterances
            subtract the mean and divide by the st dev for each frame of the selected phoneme""")
    info_norm.pack(side="top")

    info_frame.place(anchor="center", relx=.5, rely=.5)


def _hide_information_screen():
    """Destroy the information screen
    """
    info_frame.destroy()


def _set_praat_path(text_widget_praat, new_focus):
    """Set the new praat path in the model.
    Set the focus of the application on the parameter new_focus
    @called by: internal

    Args:
        text_widget_praat (tk.Text): get the set praat path
        new_focus (tk.Widget): set the focus to
    """
    model.set_praat_path(text_widget_praat.get("0.0", tk.END).strip())
    new_focus.focus_set()



def start_view():
    """Start the root mainloop.
    Add protocol to execute model json-save function on window closing
    @called by: controller
    """
    root.protocol("WM_DELETE_WINDOW", _end_view)

    root.mainloop()


def _end_view():
    """Too call on shutting down to program
    @called by: internal
    """
    model.save_config_file()
    root.destroy()


def get_choosen_files():
    """Ask user to provide files
    @called by: DeathStar

    Returns:
        (str): tuple of all filenames
    """
    # filenames = filedialog.askopenfilenames(initialdir=model.default_file_path,
    #                                         title="Select your wavs and TextGrid files",
    #                                         filetypes=(("All files", "*.*"), ("wavs", "*.wav"), ("TextGrids", "*.TextGrid")))
    filenames = ["/Users/frederickkukla/Projects/SpeakerRecognitionProject/resources/data/0023/E_0023_recordingNr_2.TextGrid",
                 "/Users/frederickkukla/Projects/SpeakerRecognitionProject/resources/data/0023/E_0023_recordingNr_2.wav"]
    if len(filenames) > 0:
        model.set_def_file_path('/'.join(filenames[0].split('/')[: -1]))
    return filenames



#########
### all warning/error methods
#########
def _show_error(message: str):
    """Show a messagebox (python module) warning (treated as error here). TODO improve this

    Args:
        message (str): message to display
    """
    messagebox.showwarning(conf.app_name + " error", message)


def show_warning(message: str):
    """Show a messagebox (python module) info (treated as warning here). TODO improve this
    @called by: internal and DeathStar

    Args:
        message (str): message to display
    """
    messagebox.showinfo(conf.app_name + " warning", message)


def display_MFCC_file_warning(mfcc_creation_problem):
    """Show a warning or error, depending on the nature of the MFCC-creation-problem
    @called by: DeathStar

    Args:
        mfcc_creation_problem ([ (str, config.ErrorMessages) ]): all error messages accummulated through the MFCC creation process

    Returns:
        bool: False if MFCCs could not be calculated
    """
    for _, err_message in mfcc_creation_problem:
        if err_message == config.ErrorMessages.MFCC_FILES_EXIST:
            show_warning(config.ErrorMessages.MFCC_FILES_EXIST.value)
        elif err_message == config.ErrorMessages.MISSING_PRAAT_PATH:
            _show_error(config.ErrorMessages.MISSING_PRAAT_PATH.value)
            return False
