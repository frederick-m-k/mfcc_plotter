
import tkinter as tk

import config

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

################
#### deprecated
################
class CustomLegend(tk.Frame):
    """deprecated
    """

    def __init__(self, master, speaker1, speaker2, phonemes, lambda_func, configuration):
        tk.Frame.__init__(self, master)

        phonem1 = phonemes[0]
        phonem2 = phonemes[1]
        phonem3 = phonemes[2]
        phonem4 = phonemes[3]

        self.all_plots = dict()

        self.create_legend_entry(lambda_func, speaker1, phonem1,
                                 configuration, config.ColorCoding.CAT1.value, True).pack(side="top")

        self.create_legend_entry(lambda_func, speaker1, phonem2,
                                 configuration, config.ColorCoding.CAT2.value, False).pack(side="top")

        self.create_legend_entry(lambda_func, speaker2, phonem3,
                                 configuration, config.ColorCoding.CAT3.value, False).pack(side="top")

        self.create_legend_entry(lambda_func, speaker2, phonem4,
                                 configuration, config.ColorCoding.CAT4.value, False).pack(side="top")

    def create_legend_entry(self, lambda_func, speaker, phonem, configuration, colorCoding, first):
        entryFrame = tk.Frame(self)

        check = tk.Checkbutton(entryFrame, text="", command=lambda: lambda_func(
            speaker, phonem, self), variable=tk.IntVar())
        check.pack(side="left")
        if first:
            check.select()

        firstText = tk.Label(entryFrame, text=speaker + " - ",
                             font=(configuration.font_family, configuration.font_size))
        firstText.pack(side="left")

        secondText = tk.Label(entryFrame, text=phonem, font=(
            configuration.treeview_font, configuration.font_size))
        secondText.pack(side="left")

        plot = self.legend_extension(entryFrame, speaker, phonem, colorCoding)
        plot.get_tk_widget().pack(side="right")

        return entryFrame

    def legend_extension(self, frame, spk, pho, colorCoding):
        """[summary]

        Args:
            frame (tk.Frame): the master on which to place the figure on

        Returns:
            FigureCanvasTkAgg: the plot in a weird format
        """
        fig, ax = plt.subplots(1, 1, figsize=(0.5, 0.5))
        plot = FigureCanvasTkAgg(fig, frame)

        self.all_plots[(spk, pho)] = (plot, ax.fill_between(x=[-1, 1], y1=-1, y2=1, color=colorCoding[0], edgecolor=colorCoding[1],
                                                            facecolor=colorCoding[2], alpha=0.9, hatch=colorCoding[5]))
        # TODO set alpha on colorCoding[4] again, if update_alpha is working
        ax.set_axis_off()

        plot.draw()

        return plot

    def update_legend(self, spk, pho, alpha):
        plot, polyColl = self.all_plots[spk, pho]

        polyColl.set_alpha(alpha)
        plot.draw()
