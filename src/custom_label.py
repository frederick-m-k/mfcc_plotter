
import tkinter as tk


class CustomLabel(tk.Frame):

    def __init__(self, master, text, justify="center"):
        super().__init__(master, pady=2)

        if '\n' in text:
            for part in text.split('/n'):
                lab = tk.Label(self, justify=justify, text=part)
                lab.pack(side="top")
        else:
            lab = tk.Label(self, justify=justify, text=text)
            lab.pack(side="top")
