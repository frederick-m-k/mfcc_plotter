
import tkinter as tk


class CustomLabel(tk.Frame):
    """Tkinter Frame which adds several labels vertically on one another depending on a given text
    @called by: view
    """

    def __init__(self, master, text: str, justify="center"):
        """Init a Frame to hold several labels vertically on one another
        @called by: view

        Args:
            master (tkinter object): e.g. tk.Frame
            text (str): to put into labels
            justify (str, optional): Defaults to "center".
        """
        super().__init__(master, pady=2)

        if '\n' in text:
            for part in text.split('/n'):
                lab = tk.Label(self, justify=justify, text=part)
                lab.pack(side="top")
        else:
            lab = tk.Label(self, justify=justify, text=text)
            lab.pack(side="top")
