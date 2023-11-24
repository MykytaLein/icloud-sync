import tkinter  as tk
import logic

class MainWindow(tk.Frame):
    def __init__(self: tk.Frame, master: tk.Tk):
        tk.Frame.__init__(self, master=master)
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)

        lastRunDict = logic.load_last_run_info()
        lastRunDate     = lastRunDict['last_run_date']
        lastRunDateFrom = lastRunDict['date_from']
        lastRunDateTo   = lastRunDict['date_to']
