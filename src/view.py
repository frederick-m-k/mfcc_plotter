
import math
import sys
import tkinter as tk
from tkinter import ttk, font, messagebox
from tkinter import filedialog
from tkinter.constants import NO
from PIL import Image, ImageTk

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config
from config import logging as logging
import numpy as np
from customLegend import CustomLegend
from deathStar import DeathStar
from custom_label import CustomLabel

import model
from category import Category

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

    # title = tk.Label(root, text=conf.app_name, font=(
    #     conf.font_family, conf.brand_size - 4), justify="left")
    # title.grid(column=0, columnspan=2, row=2, padx=25, pady=25)

    # font stuff
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family=conf.treeview_font, size=conf.font_size)

    default_font = font.nametofont("TkHeadingFont")
    default_font.configure(family=conf.font_family, size=conf.font_size)

    im = Image.open("src/imgs/information-button.png").resize((25, 25))
    info_im = ImageTk.PhotoImage(im)

    init_start_screen()

    init_information_screen()


def init_choose_file(browse_files):
    global button_choose_file
    button_choose_file = tk.Button(
        root, text="Choose 2 wavs and 2 TextGrids", font=(conf.font_family, conf.font_size), command=browse_files)
    button_choose_file.place(anchor="center", relx=.5, rely=.5)


def init_start_screen():
    '''
        Initialize a start screen with some background information
    '''
    start_frame = tk.Frame(root)

    start_frame.place(anchor="center", relx=.5, rely=.5)

    start_prompt = tk.Label(start_frame, text=conf.start_prompt_text, font=(
        conf.font_family, conf.font_size))
    start_button = tk.Button(start_frame, text="Start the app", font=(conf.font_family, conf.font_size),
                             command=lambda: switch_toDoubleDisplay(start_frame))  # switch_to_chooseFile(start_frame, browse_files)

    start_prompt.pack(side="top")
    start_button.pack(side="top")


def switch_toDoubleDisplay(frame):
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
                             command=lambda: switch_display(merge_button, left_star, right_star, merged_star))
    merge_button.place(anchor="center", relx=.5, rely=.25)

    lab = tk.Label(frame, image=info_im)
    lab.place(anchor="center", relx=0.98, rely=.25)
    lab.bind("<Button-1>", lambda event: show_information_screen(event))


def get_range_of_stars():
    """

    Returns:
        list[float]: x_range[bottom, top]
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


def reload_other_statistics(star2not_reload):
    for star in stars:
        if star == star2not_reload:
            continue

        star.reload_statistics()


def switch_display(button, left_star, right_star, merged_star):
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


def switch_to_chooseFile(frame, chooseFile_func):
    frame.place_forget()
    init_choose_file(chooseFile_func)


def init_all_options(speaker2phoneme):
    button_choose_file.place_forget()
    # button_choose_file.place(x=10, y=10)
    # TODO replace button for choosing files and add functionality for clearing existing data

    main_frame = tk.Frame(root)
    main_frame.place(anchor="center", relx=.5, rely=.5)

    phoneme_prompt = tk.Label(main_frame, text="Choose your phonemes",
                              font=(conf.font_family, conf.heading_size), pady=15)
    phoneme_prompt.pack(side="top")
    _create_phoneme_options(main_frame, speaker2phoneme)

# phoneme options


def _create_phoneme_options(main_frame, speaker2phoneme):
    '''
    Create the list boxes for choosing the phoneme labels
    '''
    # global customFont
    box_frame = tk.Frame(main_frame)
    box_frame.pack(side="top")
    width = int(main_screen_width / 8)

    for speaker, phonemes in speaker2phoneme.items():
        tree_labels.append(speaker)
        for _ in range(2):
            option = ttk.Treeview(
                box_frame, columns=speaker, displaycolumns=speaker)
            option.column("#0", width=0, stretch=NO)
            option.column(speaker, width=width, anchor="center", stretch=True)
            option.heading(speaker, text=speaker, anchor="center")
            for phoneme in phonemes:
                option.insert('', 'end', text='', values=(phoneme))
            option.pack(side="left")
            tree2selected[option] = ""
            option.bind("<Button-1>", lambda event,
                        tree=option: handle_phoneme_selection(event, tree, main_frame))


def handle_phoneme_selection(event, tree, main_frame):
    '''

    '''
    # TODO remove all empty segments "" from TextGrids -> maybe at the parser
    item = tree.identify("item", event.x, event.y)
    label = tree.item(item, "values")
    label = label[0]
    tree2selected[tree] = label

    if check_tree_selection4integrity():  # all labels selected

        children = main_frame.winfo_children()
        # TODO this is hardcoded. Make it better, when you have time
        for i in range(len(children)):
            if i > 1:
                children[i].destroy()
        selected_per_Frame.clear()

        if check_tree_selection4SamePhoneme():
            show_error(config.ErrorMessages.SAME_PHONEME.value)
            return

        # create the button to display the MFCCs
        button_display_mfccs = tk.Button(main_frame, text="Display MFCCs",
                                         font=(conf.font_family, conf.font_size), command=lambda: prep_visualization(main_frame))
        button_display_mfccs.pack(side="bottom")
        button_display_mfccs["state"] = "disabled"
        # _create_norm_options(
        #     main_frame, tree2selected.values(), button_display_mfccs)
        _create_mfccCalculation_options(main_frame, button_display_mfccs)


def check_tree_selection4SamePhoneme():
    '''

    '''
    tmp = list(tree2selected.values())
    return ((tmp[0] == tmp[1]) or (tmp[2] == tmp[3]))


def check_tree_selection4integrity():
    '''
        check, if all trees got a selected label
        return True if that's correct
    '''
    return_val = True
    for _, value in tree2selected.items():
        if value == "":
            return_val = False
    return return_val


def init_information_screen():
    pass


def show_information_screen(event):
    global info_frame
    width = main_screen_width - 0.1*main_screen_width
    canvas_width = width - 0.05 * width
    main_height = main_screen_height - 0.1*main_screen_height
    info_frame = tk.Frame(root, background="white",
                          highlightbackground="grey", highlightthickness=4, width=width, height=main_height - 0.1*main_height)

    close_button = tk.Button(info_frame, text="Close",
                             command=hide_information_screen)
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
                                  command=lambda: set_praat_path(input_praat, close_button))
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

    # canvas = tk.Canvas(info_frame, width=width - 0.05 *
    #                    width, height=10, bg="white")
    # canvas.create_line(0.05*canvas_width, 5,
    #                    canvas_width - 0.05*canvas_width, 5)
    # canvas.pack(side="top")

    # flat_joke = CustomLabel(
    #     info_frame, justify="center", text="What is the most favorite data type of a ghost?"
    # )
    # flat_joke.pack(side="top")
    # flat_joke.bind()

    info_frame.place(anchor="center", relx=.5, rely=.5)


def hide_information_screen():
    info_frame.destroy()


def set_praat_path(text_widget_praat, new_focus):
    """Set the new praat path in the model.
    Set the focus of the application on the parameter new_focus

    Args:
        text_widget_praat (tk Text): get the set praat path
        new_focus (tk Widget): set the focus to
    """
    model.set_praat_path(text_widget_praat.get("0.0", tk.END).strip())
    new_focus.focus_set()


def prep_visualization(main_frame):
    # remove all options and stuff
    main_frame.place_forget()

    # normalize in the model
    # if selected_per_Frame[config.Norm] == config.Norm.NO_NORM.value:
    #     spk2phos2frames = no_norm_mfccs(selected_per_Frame[config.Calc])
    # elif selected_per_Frame[config.Norm] == config.Norm.NORM_SPEAKER.value:
    #     spk2phos2frames = norm_mfccs_rem_speaker(
    #         selected_per_Frame[config.Calc])
    # elif selected_per_Frame[config.Norm] == config.Norm.NORM_PHONEME.value:
    #     spk2phos2frames = norm_mfccs_rem_phonem(
    #         selected_per_Frame[config.Calc], list(tree2selected.values()))
    # else:
    #     print(selected_per_Frame[config.Norm])

    # show death star
    # display_mfccs(spk2phos2frames)


def _create_mfccCalculation_options(main_frame, button_display_mfccs):
    '''
        create a treeview to display options of mfcc calculation
        and add it to the given parameter main_frame
    '''
    box_frame = tk.Frame(main_frame)
    box_frame.pack(side="bottom", pady=20)

    calc_options = ["praat", "librosa"]

    column_name = "calc_option"
    width = int(main_screen_width / 8)
    options = ttk.Treeview(box_frame, columns=column_name,
                           height=len(calc_options))
    options.column("#0", width=0, stretch=NO)
    options.column(column_name, width=width, anchor="center")
    options.heading(
        column_name, text="Choose mfcc calculation option", anchor="center")
    for calc_option in calc_options:
        options.insert('', "end", text='', values=(calc_option, ))
    # options.bind("<Button-1>", lambda event,
    #              tree=options: handle_options(event, tree, main_frame, button_display_mfccs))
    options.pack(side="left")


def start_view():
    """Start the root mainloop.
    Add protocol to execute model json-save function on window closing
    """
    root.protocol("WM_DELETE_WINDOW", end_view)

    root.mainloop()


def end_view():
    model.save_config_file()
    root.destroy()


def display_mfccs(spk2phos2frames, n_mfccs=conf.n_mfccs):
    global global_min, global_max

    speaker1 = tree_labels[0]
    speaker2 = tree_labels[1]
    label1 = list(tree2selected.values())[0]
    label2 = list(tree2selected.values())[1]
    label3 = list(tree2selected.values())[2]
    label4 = list(tree2selected.values())[3]
    mfccs1 = spk2phos2frames[speaker1][label1]
    mfccs2 = spk2phos2frames[speaker1][label2]
    mfccs3 = spk2phos2frames[speaker2][label3]
    mfccs4 = spk2phos2frames[speaker2][label4]
    all_graphs[(speaker1, label1)] = Category(
        speaker1, label1, mfccs1, first=True)
    all_graphs[(speaker1, label2)] = Category(
        speaker1, label2, mfccs2, first=True)
    all_graphs[(speaker2, label3)] = Category(
        speaker2, label3, mfccs3, first=False)
    all_graphs[(speaker2, label4)] = Category(
        speaker2, label4, mfccs4, first=False)

    set_phonemes[(speaker1, label1)] = False
    set_phonemes[(speaker1, label2)] = False
    set_phonemes[(speaker2, label3)] = False
    set_phonemes[(speaker2, label4)] = False

    global_min, global_max = get_global_min_max(speaker1, label1)

    all_graphs[(speaker1, label1)].set_color(config.ColorCoding.CAT1.value)
    all_graphs[(speaker1, label2)].set_color(config.ColorCoding.CAT2.value)

    all_graphs[(speaker2, label3)].set_color(config.ColorCoding.CAT3.value)
    all_graphs[(speaker2, label4)].set_color(config.ColorCoding.CAT4.value)

    plt.rcParams["hatch.linewidth"] = 4.0
    plt.rcParams.update({'font.family': conf.font_family})

    create_frame()
    legend = create_legend(label1, label2, label3, label4, speaker1, speaker2)

    plot_sub(speaker1, label1, first=True)
    plot_sub(speaker1, label2, first=True)
    plot_sub(speaker2, label3, first=False)
    plot_sub(speaker2, label4, first=False)

    update_plot(speaker1, label1, legend)


def create_legend(phonem1, phonem2, phonem3, phonem4, speaker1, speaker2):
    legend = CustomLegend(root, speaker1, speaker2, [
        phonem1, phonem2, phonem3, phonem4], update_plot, conf)

    legend.place(anchor=tk.N, relx=.85, rely=.15)

    return legend


def create_frame():
    # 7 for small MacBookPro
    # 14 for BigMac display
    global fig, ax, plot
    figSize = math.floor(main_screen_width / 240)
    # print(figSize)
    fig, ax = plt.subplots(
        figsize=(figSize, figSize), dpi=100, subplot_kw=dict(polar=True))

    plot = FigureCanvasTkAgg(fig, root)
    plot.get_tk_widget().place(anchor="center", relx=.5, rely=.5)

    plot_mfccs()


def plot_mfccs(n_mfccs=conf.n_mfccs):
    global ax
    temp_ang = conf.angles[:-1]
    temp2_ang = []
    for ang in temp_ang:
        temp2_ang.append(ang + (1/(n_mfccs*2)*(2*np.pi)))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    global theta_labels
    _, theta_labels = ax.set_thetagrids(np.degrees(temp2_ang), conf.labels, fontsize=12, rotation_mode="default",
                                        ha="center", va="center", rotation=45)

    ax.set_rlabel_position(5)
    ax.set_rmax(20)


def plot_sub(speaker, phonem, first, n_mfccs=conf.n_mfccs):
    ''' first is a @param to determine, if the mfccs should be plotted in the first or second half pie piece '''
    global global_min, global_max
    category = all_graphs[(speaker, phonem)]
    half_pie_piece = (1/(n_mfccs*2)*(2*np.pi))
    for i in range(n_mfccs):
        if first:
            updated_sec_angle = conf.angles[i+1] - half_pie_piece
            all_graphs[(speaker, phonem)].add_graphic(ax.fill_betweenx([category.values[i], global_min, global_max, category.values[i+n_mfccs]],
                                                                       conf.angles[
                                                                           i], updated_sec_angle, color=category.main_color, edgecolor=category.edgecolor,
                                                                       facecolor=category.facecolor, alpha=category.alpha, hatch=category.hatch))
            all_graphs[(speaker, phonem)].add_graphic(ax.fill_betweenx([category.medians[i], global_min, global_max, category.medians[i]], conf.angles[i],
                                                                       updated_sec_angle, color=category.median_color, alpha=0.2))
        else:
            updated_first_angle = conf.angles[i] + half_pie_piece
            all_graphs[(speaker, phonem)].add_graphic(ax.fill_betweenx([category.values[i], global_min, global_max, category.values[i+n_mfccs]],
                                                                       updated_first_angle, conf.angles[
                                                                           i+1], color=category.main_color, edgecolor=category.edgecolor,
                                                                       facecolor=category.facecolor, alpha=category.alpha, hatch=category.hatch))
            all_graphs[(speaker, phonem)].add_graphic(ax.fill_betweenx([category.medians[i], global_min, global_max, category.medians[i]], updated_first_angle,
                                                                       conf.angles[i+1], color=category.median_color, alpha=0.2))


def update_alpha(speaker, phonem, alpha):
    for i in range(len(all_graphs[speaker, phonem].all_graphics)):
        if i % 2 == 1:  # mean
            all_graphs[(speaker, phonem)].all_graphics[i].set_alpha(alpha)
        else:  # area between quantiles
            all_graphs[(speaker, phonem)].all_graphics[i].set_alpha(alpha)


def update_plot(speaker, phonem, legend, n_mfccs=conf.n_mfccs):
    global fig, ax
    global global_min, global_max

    ax.clear()
    plot_mfccs()

    # phonem 2 always has a transparent component in their plot
    # therefore, it should be plotted after phonem 1,
    #   so that phonem 1 can be seen through
    plot_sub(tree_labels[0], list(tree2selected.values())[0], first=True)
    plot_sub(tree_labels[0], list(tree2selected.values())[1], first=True)
    plot_sub(tree_labels[1], list(tree2selected.values())[2], first=False)
    plot_sub(tree_labels[1], list(tree2selected.values())[3], first=False)

    set_phonemes[(speaker, phonem)] = not set_phonemes[(speaker, phonem)]
    for (sp, pho), set in set_phonemes.items():
        if set:
            update_alpha(sp, pho, alpha=0.9)
            legend.update_legend(sp, pho, 0.9)
        else:
            update_alpha(sp, pho, alpha=0.2)
            legend.update_legend(sp, pho, 0.2)

    for i in conf.angles:
        ax.fill_betweenx([global_min, global_max], i,
                         i, color="black", lw=2.5)

    for i in conf.angles:
        ax.fill_betweenx([global_min, global_max], i+1/(n_mfccs*2)*(2*np.pi),
                         i+1/(n_mfccs*2)*(2*np.pi), color="#d2d2d2", lw=1.5)

    plot.draw()


def get_choosen_files():
    """Ask user to provide files

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


def get_global_min_max(default_speaker, default_label):
    glob_min = all_graphs[(default_speaker, default_label)].min
    glob_max = all_graphs[(default_speaker, default_label)].max
    for cat in all_graphs.values():
        if cat.min < glob_min:
            glob_min = cat.min
        if cat.max > glob_max:
            glob_max = cat.max
    return glob_min, glob_max

# all warning/error methods


def show_error(message):
    messagebox.showwarning(conf.app_name + " error", message)


def show_warning(message):
    messagebox.showinfo(conf.app_name + " warning", message)


def display_MFCC_file_warning(mfcc_creation_problem):
    """Show a warning or error, depending on the nature of the MFCC-creation-problem

    Args:
        mfcc_creation_problem ([ (str, config.ErrorMessages) ]): all error messages accummulated through the MFCC creation process

    Returns:
        bool: False if MFCCs could not be calculated
    """
    for _, err_message in mfcc_creation_problem:
        if err_message == config.ErrorMessages.MFCC_FILES_EXIST:
            show_warning(config.ErrorMessages.MFCC_FILES_EXIST.value)
        elif err_message == config.ErrorMessages.MISSING_PRAAT_PATH:
            show_error(config.ErrorMessages.MISSING_PRAAT_PATH.value)
            return False
