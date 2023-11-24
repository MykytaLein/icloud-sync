from tkinter        import (Tk, Frame, Label, Button, Entry, 
                            Checkbutton, BooleanVar, StringVar)
from tkinter.ttk    import Combobox
from tkcalendar     import DateEntry
from datetime       import date
import json

# from json import load


class MainWindow(Frame):
    def __init__(self: Frame, master: Tk=None):
        Frame.__init__(self, master=master)