
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


import numpy as np
import math

import tkinter as tk
from tkinter import NO, ttk
from category import Category

import view
import model
import config


class DeathStar(tk.Frame):
    """Class as a wrapper for a death-star plot and its corresponding selection menus
    @called by: view
    """

    def __init__(self, master, figSize: int, config_obj: config.Config, colorCoding: config.ColorCoding, screenWidth: float, screenHeight: float, root):
        """Initiate a DeathStar holding a death-star plot and its corresponding selection menu
        @called by: view

        Args:
            master (tkinter object): e.g. tk.Frame
            figSize (int): to set the size of the death-star plot. TODO!!
            config_obj (config.Config): holding configuration variables
            colorCoding (config.ColorCoding): holding color information for this specific DeathStar
            screenWidth (float)
            screenHeight (float)
            root (tkinter object): root of the whole system
        """
        tk.Frame.__init__(self, master)

        self.rec_names = ""

        self.menu_frame = tk.Frame(
            self, highlightcolor=colorCoding.value[6], highlightbackground=colorCoding.value[6], highlightthickness=4)
        self.left_frame = tk.Frame(self.menu_frame)

        plt.rcParams["hatch.linewidth"] = 4.0
        self.plot = None
        self.ax = None
        self.rect_id = None

        self.norm_treeview = None
        self.norm_remPhoneme_ID = ""

        self.librosa_mfccs = dict()
        self.praat_mfccs = dict()

        self.calculation_option = ""
        self.norm_option = ""
        self.selected_phoneme = ""
        self.current_coef = -1

        self.config = config_obj
        self.colorCoding = colorCoding.value

        self.my_width = screenWidth / 2
        self.my_height = screenHeight

        self.root = root

        self.got_data = False
        self.currently_seen = False
        self.statistics_visible = False

        self.current_mfccs = []
        self.left_mfccs = []
        self.right_mfccs = []

        if not colorCoding.value[7]:
            self._init_menus(config_obj)
        self._init_star(figSize)

    def _init_menus(self, conf: config.Config):
        """Initiate the selection menu
        @called by: internal

        Args:
            conf (config.Config): _description_
        """
        button_choose_file = tk.Button(
            self.left_frame, text="Choose wav\nand TextGrid", font=(conf.font_family, conf.font_size), command=self._browse_files)
        button_choose_file.pack(side="bottom")
        self.left_frame.pack(side="left", padx=5)

        self.menu_frame.pack(side="top")

    def _fill_menus(self, recName2phoneme: dict):
        """Firstly, clear all existing graphical content of the selection menu.
        Afterwards, refill the seection menu again
        @called by: internal

        Args:
            recName2phoneme (dict(str, [str]) )
        """
        [ch.pack_forget() for ch in self.menu_frame.winfo_children()]
        if len(self.left_frame.winfo_children()) > 1:
            self.left_frame.winfo_children()[1].destroy()

        self._addRecLabel(
            ",\n".join([spk for spk in list(recName2phoneme.keys())]))
        self.left_frame.pack(side="left")

        pho_frame = self._create_phoneme_options(self.menu_frame, recName2phoneme)
        pho_frame.pack(side="left")

        calcNorm_frame = tk.Frame(self.menu_frame)
        calc_frame = self._create_calculation_options(calcNorm_frame)
        norm_frame = self._create_norm_options(calcNorm_frame)
        calc_frame.pack(side="top", pady=18)
        norm_frame.pack(side="bottom")

        calcNorm_frame.pack(side="left", padx=10)

    def _locate_mfcc_on_mouse_click(self, event):
        """Find the mfcc whose area was clicked on by user
        @called by: internal

        Args:
            event (MouseEvent): MouseEvent which holds x and y pixels as well as xdata and ydata, coordinates on the star in radians
        """
        n_mfccs = 13

        if event.xdata == None or event.ydata == None:
            return

        if self.currently_seen == False:
            return

        step = (math.pi*2) / n_mfccs
        for i in range(n_mfccs):
            if event.xdata > 0:
                if event.xdata >= step*i and event.xdata <= step*(i+1):
                    self._plot_statistics_by_coefficient(i+1-1)
                    break
            else:
                if event.xdata <= (-1)*step*i and event.xdata >= (-1)*step*(i+1):
                    self._plot_statistics_by_coefficient(n_mfccs-i-1)
        self.statistics_visible = True

    def _plot_statistics_by_coefficient(self, coef: int):
        """Plot statistical information on one mfcc dimension
        Differentiating between merged star and non-merged star
        @called by: internal

        Args:
            coef (int): coefficient to plot information of
        """
        self.current_coef = coef
        x_range = view.get_range_of_stars()

        if self.colorCoding[7]:     # =merged star
            left_mf = [frame[coef] for frame in self.left_mfccs]
            right_mf = [frame[coef] for frame in self.right_mfccs]

            self.stat_frame = tk.Frame(
                self.root, background="white", highlightbackground="grey", highlightthickness=4)
            upper_frame = tk.Frame(self.stat_frame)
            # textual information
            left_lab = tk.Label(upper_frame, justify="center",
                                text="coefficent " +
                                str(coef+1) + ";\n mean: " +
                                str(np.round(np.mean(left_mf), 2)) + "; median: " +
                                str(np.round(np.median(left_mf), 2)) + "; st dev: " + str(np.round(np.std(left_mf), 2)) +
                                "; \n number of samples: " + str(len(left_mf)))
            left_lab.pack(side="left", padx=15)

            right_lab = tk.Label(upper_frame, justify="center",
                                 text="coefficent " +
                                 str(coef+1) + ";\n mean: " +
                                 str(np.round(np.mean(right_mf), 2)) + "; median: " +
                                 str(np.round(np.median(right_mf), 2)) + "; st dev: " + str(np.round(np.std(right_mf), 2)) +
                                 "; \n number of samples: " + str(len(right_mf)))
            right_lab.pack(side="right", padx=15)

            # close button
            close_button = tk.Button(upper_frame, text="Close",
                                     command=self._hide_statistics)
            close_button.pack(side="right")

            upper_frame.pack(side="top")

            # plots
            fig = Figure()

            # histogram
            ax_hist = fig.add_subplot(221, label="right")
            ax_hist.hist([left_mf, right_mf], color=[
                         config.ColorCoding.COMB1.value[1], config.ColorCoding.COMB2.value[2]])
            ax_hist.set_ylabel("Occurrence")
            ax_hist.set_xlim(x_range)
            ax_hist.set_xlabel("MFCC values")

            # ecdf-plot
            ax_ec = fig.add_subplot(223, label="right")
            ax_ec.scatter(np.sort(left_mf), np.arange(
                1, len(left_mf)+1) / len(left_mf), color=config.ColorCoding.COMB1.value[1])
            ax_ec.scatter(np.sort(right_mf), np.arange(
                1, len(right_mf)+1) / len(right_mf), color=config.ColorCoding.COMB2.value[2])
            ax_ec.set_ylabel("Fraction")  # TODO better name than fraction?
            ax_ec.set_xlim(x_range)

            # boxplot
            ax_box = fig.add_subplot(122, label="left")
            ax_box.boxplot([left_mf, right_mf])[
                "medians"][0].set(color=config.ColorCoding.COMB1.value[1])
            ax_box.set_ylabel("MFCC values")
            ax_box.set_xticklabels([str(coef+1), str(coef+1)])
            ax_box.set_ylim(x_range)

            fig.tight_layout()

            stat_plot = FigureCanvasTkAgg(fig, self.stat_frame)
            stat_plot.get_tk_widget().configure(highlightbackground="white")
            stat_plot.get_tk_widget().pack(side="bottom", pady=20)

            self.stat_frame.place(
                anchor="center", relx=.5, rely=.6)

        else:                       # =non-merged stars
            mfccs = [frame[coef] for frame in self.current_mfccs]

            self.stat_frame = tk.Frame(self.root, background="white",
                                       highlightbackground="grey", highlightthickness=4)

            upper_frame = tk.Frame(self.stat_frame)
            # textual information
            text_info = tk.Label(upper_frame, justify="center",
                                 text="coefficent " +
                                 str(coef+1) + ";\n mean: " +
                                 str(np.round(np.mean(mfccs), 2)) + "; median: " +
                                 str(np.round(np.median(mfccs), 2)) + "; st dev: " + str(np.round(np.std(mfccs), 2)) +
                                 "; \n number of samples: " + str(len(mfccs)))
            text_info.pack(side="left", padx=15)

            # close button
            close_button = tk.Button(upper_frame, text="Close",
                                     command=self._hide_statistics)
            close_button.pack(side="right")

            upper_frame.pack(side="top")

            # plots
            fig = Figure()

            # histogram
            main_color = self.colorCoding[2] if self.colorCoding[2] != "none" else self.colorCoding[1]
            ax_hist = fig.add_subplot(221, label="right")
            ax_hist.hist(mfccs, color=main_color)
            ax_hist.set_ylabel("Occurrence")
            ax_hist.set_xlim(x_range)
            ax_hist.set_xlabel("MFCC values")

            # ecdf-plot
            ax_ec = fig.add_subplot(223, label="right")
            ax_ec.scatter(np.sort(mfccs), np.arange(
                1, len(mfccs)+1) / len(mfccs), color=main_color)
            ax_ec.set_ylabel("Fraction")  # TODO better name than fraction?
            ax_ec.set_xlim(x_range)

            # boxplot
            ax_box = fig.add_subplot(122, label="left")
            ax_box.boxplot(mfccs)[
                "medians"][0].set(color=self.colorCoding[3])
            ax_box.set_ylabel("MFCC values")
            ax_box.set_xticklabels([str(coef+1)])
            ax_box.set_ylim(x_range)

            fig.tight_layout()

            stat_plot = FigureCanvasTkAgg(fig, self.stat_frame)
            stat_plot.get_tk_widget().configure(highlightbackground="white")
            stat_plot.get_tk_widget().pack(side="bottom", pady=20)

            self.stat_frame.place(
                anchor="center", relx=.25 if self.colorCoding[8] == "left" else .75, rely=.6)

            view.reload_other_statistics(self)

    def reload_statistics(self):
        """Reload the statistical display of one mfcc dimension
        @called by: view
        """
        if self.statistics_visible:
            self.stat_frame.destroy()
            self._plot_statistics_by_coefficient(self.current_coef)

    def _hide_statistics(self):
        """Hide the displayed statistical information on one mfcc dimension
        @called by: internal
        """
        self.stat_frame.destroy()
        self.statistics_visible = False

    def _init_star(self, figSize: int):
        """Initiate the death-star plot
        @called by: internal

        Args:
            figSize (int): to set the size of the death-star plot
        """
        fig, self.ax = plt.subplots(
            figsize=(figSize, figSize), dpi=100, subplot_kw=dict(polar=True))

        self.plot = FigureCanvasTkAgg(fig, self)
        self.plot.figure.canvas.mpl_connect("button_press_event",
                                            self._locate_mfcc_on_mouse_click)

        self.plot.get_tk_widget().configure(highlightbackground="white")
        self.plot.get_tk_widget().pack(side="bottom", pady=20)

        self._fillStarOutline()

    def _fillStarOutline(self):
        """Fill the outline of the death-star plot
        @called by: internal
        """
        temp_ang = self.config.angles[:-1]
        temp2_ang = []
        for ang in temp_ang:
            temp2_ang.append(ang + (1/(self.config.n_mfccs*2)*(2*np.pi)))
        self.ax.set_theta_offset(np.pi / 2)
        self.ax.set_theta_direction(-1)

        _, theta_labels = self.ax.set_thetagrids(np.degrees(self.config.angles[:-1]),  # self.config.labels,
                                                 fontsize=10, fontfamily=self.config.font_family)  # , rotation_mode="anchor", rotation=90)

        self.ax.tick_params(axis="x", labelrotation=0)
        labels = self.ax.set_xticklabels(
            ["MFCC"+str(i) for i in range(1, self.config.n_mfccs+1)])

    def _addRecLabel(self, rec_name: str):
        """Add a tk.Label with the name of the recording
        @called by: internal

        Args:
            rec_name (str)
        """
        spkLabel = tk.Label(self.left_frame, text=rec_name, font=(
            self.config.font_family, self.config.font_size, "bold"))

        spkLabel.pack(side="top", pady=10)

    def _create_phoneme_options(self, main_frame, recName2phoneme: dict):
        """Create the phoneme options graphical menu
        TODO remove variable speaker. It is unnecessary. With this, the dict recName2phoneme can be replaced with a list of phonemes
        @called by: internal

        Args:
            main_frame (tk.Frame)
            recName2phoneme (dict(str, [str]))
        """
        phoneme_frame = tk.Frame(main_frame)
        phonemes = sorted(
            list(set([v for val in list(recName2phoneme.values()) for v in val])))

        heading = tk.Label(phoneme_frame, text="Phoneme")

        tmp = tk.StringVar()
        tmp.set("all")
        options = tk.OptionMenu(
            phoneme_frame, tmp, *["all"] + phonemes,
            command=lambda event: view.on_option_change(event, tmp, self))
        options.config(width=len(config.Norm.NO_NORM.value))
        self.selected_phoneme = "all"

        heading.pack(side="top")
        options.pack(side="bottom", pady=5)
        return phoneme_frame

    def _create_calculation_options(self, parent_frame: tk.Frame):
        """Create the calculation options menu
        @called by: internal

        Args:
            parent_frame (tk.Frame)
        """
        calc_options = [config.Calc.PRAAT, config.Calc.LIBROSA]

        calc_frame = tk.Frame(parent_frame)

        heading = tk.Label(calc_frame, text="Calculation")

        tmp = tk.StringVar()
        tmp.set(config.Calc.PRAAT.value)
        options = tk.OptionMenu(
            calc_frame, tmp, *[o.value for o in calc_options],
            command=lambda event: view.on_option_change(event, tmp, self))
        options.config(width=len(config.Norm.NO_NORM.value))

        self.calculation_option = calc_options[0].value

        heading.pack(side="top")
        options.pack(side="bottom")
        return calc_frame

    def _create_norm_options(self, parent_frame: tk.Frame):
        """Create the normalization options menu
        @called by: internal

        Args:
            parent_frame (tk.Frame)
        """
        norm_options = [config.Norm.REM_SPEAKER, config.Norm.NO_NORM]

        norm_frame = tk.Frame(parent_frame)

        heading = tk.Label(norm_frame, text="Normalization")

        tmp = tk.StringVar()
        tmp.set(config.Norm.NO_NORM.value)
        self.norm_treeview = tk.OptionMenu(
            norm_frame, tmp, *[o.value for o in norm_options],
            command=lambda event: view.on_option_change(event, tmp, self))
        self.norm_treeview.config(width=len(config.Norm.NO_NORM.value))

        heading.pack(side="top")

        self.norm_treeview.pack(side="bottom")

        return norm_frame


    def hide_star(self):
        """Overlap the star with a white rectangle. TODO: make better!!
        @called by: view
        """
        self.rect_id = self.plot.get_tk_widget().create_rectangle(
            -1, -1, self.my_width, self.my_height, fill="white")

    def show_star(self):
        """Show the death-star plot
        @called by: view
        """
        self.show_mfccs()
        self.rect_id = None

    def _browse_files(self):
        """User selects files. They get processed here, i.e. the mfccs get created by the model
        @called by: internal
        """
        chosen_files = view.get_choosen_files()
        err_message = model.check_file_input(chosen_files)
        if err_message != config.ErrorMessages.NO_ERROR:
            view.show_warning(err_message.value)
        else:
            self.rec_names = model.get_rec_names(chosen_files)
            mfcc_creation_errors = model.create_mfccs(
                list(chosen_files))

            if view.display_MFCC_file_warning(mfcc_creation_errors) == False:
                return

            recName2phoneme = model.get_recName2phoneme(self.rec_names)
            self.librosa_mfccs, self.praat_mfccs = model.get_all_mfccs(
                self.rec_names)

            self._fill_menus(recName2phoneme)
            self.show_mfccs()
            self.got_data = True

    def update_mfccs(self):
        """Update the mfccs based on the selected options. Also show statistics if visible
        @called by: internal and view

        Returns:
            dict(str, [[float]]): the updated MFCCs
        """
        mfccs = dict()
        if self.calculation_option == config.Calc.PRAAT.value:
            mfccs = dict.fromkeys(list(self.praat_mfccs.keys()))
            for key, val in self.praat_mfccs.items():
                mfccs[key] = list()
                for v in val:
                    mfccs[key].append(v)
        elif self.calculation_option == config.Calc.LIBROSA.value:
            mfccs = dict.fromkeys(list(self.librosa_mfccs.keys()))
            for key, val in self.librosa_mfccs.items():
                mfccs[key] = list()
                for v in val:
                    mfccs[key].append(v)

        if self.norm_option == config.Norm.REM_SPEAKER.value:
            mfccs = model.norm_mfccs_rem_speaker(mfccs)
        elif self.norm_option == config.Norm.NO_NORM.value:
            pass
        elif self.norm_option == config.Norm.REM_PHONEME.value:
            mfccs = model.norm_mfccs_rem_phonem(self.rec_names,
                                                self.calculation_option, self.selected_phoneme)

        if self.selected_phoneme == "":
            return
        elif self.selected_phoneme == "all":
            # transform the dict mfccs into a nested list of frames
            mfccs = [mfccsOfOneSamp for mfccsOfOnePho in mfccs.values()
                     for mfccsOfOneSamp in mfccsOfOnePho]
        else:
            mfccs = mfccs[self.selected_phoneme]

        self.current_mfccs = mfccs

        if self.statistics_visible:
            self._hide_statistics()
            self._plot_statistics_by_coefficient(self.current_coef)

        return mfccs

    def show_mfccs(self):
        """Display the mfccs in the death-star plot
        @called by: internal and view
        """
        self.plot.get_tk_widget().delete(self.rect_id)
        self.ax.clear()
        self._fillStarOutline()

        mfccs = self.update_mfccs()

        global_min = 0
        global_max = 0
        for val in mfccs:
            if max(val) > global_max:
                global_max = max(val)
            elif min(val) < global_min:
                global_min = min(val)
        upperquant = Category.calc_quant_mfccs(mfccs, 0.75)
        lowerquant = Category.calc_quant_mfccs(mfccs, 0.25)
        median = Category.calc_medians_mfccs(mfccs)
        for i in range(self.config.n_mfccs):
            self.ax.fill_betweenx([lowerquant[i], global_min, global_max, upperquant[i]],
                                  self.config.angles[i], self.config.angles[i+1],
                                  color=self.colorCoding[6], edgecolor="white")  # , color=category.main_color, edgecolor=category.edgecolor,
            # facecolor=category.facecolor, alpha=category.alpha, hatch=category.hatch))
            self.ax.fill_betweenx([median[i], global_min, global_max, median[i]], self.config.angles[i],
                                  self.config.angles[i+1], color=self.colorCoding[3])  # , edgecolor="white")

            self.ax.fill_betweenx([global_min, global_max], self.config.angles[i],
                                  self.config.angles[i], color="#d2d2d2", lw=2.5)
        self.ax.fill_betweenx([global_min, global_max], self.config.angles[0],
                              self.config.angles[0], color="black", lw=2.5)
        self.plot.draw()

    def give_data(self, left_mfccs: dict, right_mfccs: dict):
        """Only needed by merged star. Display the mfccs of both left and right DeathStar
        @called by: view

        Args:
            left_mfccs (dict(str, [[float]]) )
            right_mfccs (dict(str, [[float]]) )
        """
        self.left_mfccs = left_mfccs
        self.right_mfccs = right_mfccs

        self.ax.clear()
        self._fillStarOutline()

        global_min = 0
        global_max = 0
        for val in left_mfccs + right_mfccs:
            if max(val) > global_max:
                global_max = max(val)
            elif min(val) < global_min:
                global_min = min(val)

        left_color = config.ColorCoding.COMB1.value
        left_upperquant = Category.calc_quant_mfccs(left_mfccs, 0.75)
        left_lowerquant = Category.calc_quant_mfccs(left_mfccs, 0.25)
        left_median = Category.calc_medians_mfccs(left_mfccs)

        right_color = config.ColorCoding.COMB2.value
        right_upperquant = Category.calc_quant_mfccs(right_mfccs, 0.75)
        right_lowerquant = Category.calc_quant_mfccs(right_mfccs, 0.25)
        right_median = Category.calc_medians_mfccs(right_mfccs)
        for i in range(self.config.n_mfccs):
            self.ax.fill_betweenx([right_lowerquant[i], global_min, global_max, right_upperquant[i]],
                                  self.config.angles[i], self.config.angles[i+1],
                                  color=right_color[0], edgecolor=right_color[1], facecolor=right_color[2], alpha=right_color[4], hatch=right_color[5])

            self.ax.fill_betweenx([left_lowerquant[i], global_min, global_max, left_upperquant[i]],
                                  self.config.angles[i], self.config.angles[i+1],
                                  color=left_color[0], edgecolor=left_color[1], facecolor=left_color[2], alpha=left_color[4], hatch=left_color[5])

            self.ax.fill_betweenx([right_median[i], global_min, global_max, right_median[i]], self.config.angles[i],
                                  self.config.angles[i+1], color=right_color[3])  # , edgecolor="white")
            self.ax.fill_betweenx([left_median[i], global_min, global_max, left_median[i]], self.config.angles[i],
                                  self.config.angles[i+1], color=left_color[3])  # , edgecolor="white")

            self.ax.fill_betweenx([global_min, global_max], self.config.angles[i],
                                  self.config.angles[i], color="#d2d2d2", lw=2.5)

        self.ax.fill_betweenx([global_min, global_max], self.config.angles[0],
                              self.config.angles[0], color="black", lw=2.5)

        self.plot.draw()

    def check_phoneme(self, pho: str):
        """Check, if the given phoneme exists in this recording. Needed for phoneme normalization
        @called by: view

        Args:
            pho (str): the phoneme to check

        Returns:
            bool: True if phoneme exists for this recording, False if not
        """
        return pho in self.praat_mfccs.keys()

    def add_norm_remPhoneme(self):
        """Add the norm option remPhoneme to the possible options. Needed for phoneme normalization
        @called by: view
        """
        if self.norm_remPhoneme_ID == "":
            # self.norm_remPhoneme_ID = self.norm_treeview.insert('', "end", text='',
            #                                                     values=(config.Norm.REM_PHONEME.value, ))
            self.norm_treeview["menu"].add_command(
                label=config.Norm.REM_PHONEME.value)
            self.norm_remPhoneme_ID = config.Norm.REM_PHONEME.value
            # self.norm_treeview.configure(height=3)
            # self.norm_treeview.bind()

    def remove_norm_remPhoneme(self):
        """Remove the norm option remPhoneme from the possible options. Needed for phoneme normalization
        @called by: view
        """
        if self.norm_remPhoneme_ID != "":
            self.norm_treeview["menu"].delete(
                self.norm_treeview["menu"].index(self.norm_remPhoneme_ID))
            self.norm_remPhoneme_ID = ""
            # self.norm_treeview.configure(height=2)
