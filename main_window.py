import tkinter  as tk
import logic
from tkcalendar import DateEntry
from datetime   import date

class MainWindow(tk.Frame):
    def __init__(self: tk.Frame, master: tk.Tk):
        tk.Frame.__init__(self, master=master)
        self.configure_grid_weights()

        ###########################
        # Load last run information
        ###########################
        lastRunDict = logic.load_last_run_info()
        lastRunDate     = lastRunDict['last_run_date']
        lastRunDateFrom = lastRunDict['date_from']
        lastRunDateTo   = lastRunDict['date_to']
        
        #########################
        # Initialize GUI elements 
        #########################
        # Header
        header = tk.Label(master=self, text='Save Last ICloud Photos to SSD', 
                          padx=10, pady=10, bd=1, relief='sunken', font='Bauhaus 20 bold')
        
        # Date from
        dateFromLabel = tk.Label(master=self, text='Date from:', 
                                 padx=10, pady=10, anchor='w')
        dateFromInput = DateEntry(master=self, firstweekday='monday', date_pattern='dd.MM.yyyy')
        dateFromInput.set_date(lastRunDateTo)
        dateFromButton = tk.Button(master=self, text='From last run', pady=5,
                                   command=lambda:dateFromInput.set_date(lastRunDateTo))

        # Date to 
        dateToLabel = tk.Label(master=self, text='Date to:', 
                               padx=10, pady=10, anchor='w')
        dateToInput = DateEntry(master=self, firstweekday='monday', date_pattern='dd.MM.yyyy')
        dateToButton = tk.Button(master=self, text='To now', pady=5,
                                 command=lambda:dateToInput.set_date(date.today()))

        # Last run
        lastRunLabel = tk.Label(master=self, padx=10, pady=10, 
            justify="left", font='Bauhaus 15', bd=1, relief='sunken',
            text=f'Last run: {lastRunDate}\nFrom: {lastRunDateFrom}\nTo: {lastRunDateTo}')

        header.grid(row=0, column=0, columnspan=4, sticky='nswe')
        
        dateFromLabel.grid(row=1, column=0, padx=(0, 5), pady=(10, 0), sticky='we')
        dateFromInput.grid(row=1, column=1, padx=5, pady=(10, 0), sticky='we')
        dateFromButton.grid(row=1, column=2, padx=5, pady=(10, 0), sticky='nswe')

        dateToLabel.grid(row=2, column=0, padx=(0, 10), pady=(10, 40), sticky='we')
        dateToInput.grid(row=2, column=1, padx=5, pady=(10, 40), sticky='we')
        dateToButton.grid(row=2, column=2, padx=5, pady=(10, 40), sticky='nswe')

        lastRunLabel.grid(row=1, column=3, rowspan=2, padx=5, pady=(10, 40), sticky='nswe')

    def configure_grid_weights(self):
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(2,weight=1)
        self.grid_columnconfigure(3,weight=1)