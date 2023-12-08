import tkinter as tk
from tkcalendar import DateEntry
from tkinter.ttk import Combobox
from tkinter import simpledialog
import logging as log
from datetime   import date

from additional_gui import TkConsole, PopUpListBox
import logic

class MainWindow(tk.Frame):
    def __init__(self, master: tk.Tk):
        tk.Frame.__init__(self, master=master)
        self.configure_grid_weights()
        self.inputs = list()

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
        
        # Error message
        self.error = tk.Label(master=self, text='', fg='red')
        
        # Date from
        self.dateFrom = tk.StringVar()
        self.inputs.append(self.dateFrom)
        dateFromLabel = tk.Label(master=self, text='Date from:', 
                                 padx=10, pady=10, anchor='w')
        dateFromInput = DateEntry(master=self, firstweekday='monday', date_pattern='dd.MM.yyyy', textvariable=self.dateFrom)
        dateFromInput.set_date(lastRunDateTo)
        dateFromButton = tk.Button(master=self, text='From last run', pady=5,
                                   command=lambda:dateFromInput.set_date(lastRunDateTo))

        # Date to 
        self.dateTo = tk.StringVar()
        self.inputs.append(self.dateTo)
        dateToLabel = tk.Label(master=self, text='Date to:', 
                               padx=10, pady=10, anchor='w')
        dateToInput = DateEntry(master=self, firstweekday='monday', date_pattern='dd.MM.yyyy', textvariable=self.dateTo)
        dateToButton = tk.Button(master=self, text='To now', pady=5,
                                 command=lambda:dateToInput.set_date(date.today()))

        # Last run
        lastRunLabel = tk.Label(master=self, padx=10, pady=10, 
            justify="left", font='Bauhaus 15', bd=1, relief='sunken',
            text=f'Last run: {lastRunDate}\nFrom: {lastRunDateFrom}\nTo: {lastRunDateTo}')
        
        # Apple ID
        self.appleId = tk.StringVar()
        self.inputs.append(self.appleId)
        appleIdLabel = tk.Label(master=self, text='Apple ID:', 
                                padx=10, pady=10, anchor='w')
        appleIdInput = tk.Entry(master=self, textvariable=self.appleId)

        # Apple ID e-mail combobox
        self.email = tk.StringVar()
        self.inputs.append(self.email)
        eMailCmb = Combobox(master=self, textvariable=self.email, width=14,
                            values=('@icloud.com', '@gmail.com', '@gmx.de'))
        eMailCmb.current(0) 

        # Password
        self.pwd = tk.StringVar()
        self.inputs.append(self.pwd)
        pwdLabel = tk.Label(master=self, text='Password:', 
                            padx=10, pady=10, anchor='w')
        pwdInput = tk.Entry(master=self, textvariable=self.pwd)
        pwdInput.config(show='*')

        # Show/hide password checkbox
        showPass = tk.BooleanVar()
        pwdShow = tk.Checkbutton(master=self, text='Show password', width=14, anchor='w',
            variable=showPass, onvalue=True, offvalue=False, command=lambda: self.show_hide_pass_clicked(
                checkbutton=pwdShow, pwdInput=pwdInput, showPass=showPass.get()))

        # Start button
        startButton = tk.Button(master=self, text='Load photos\n from ICloud', 
                                padx=20, bg='blue', fg='white',
                                font='Bauhaus 18 bold', command=self.start_import)
        
        # Console
        self.console = TkConsole(master=self, height=4)

        header.grid(row=0, column=0, columnspan=4, sticky='nswe')

        self.error.grid(row=1, column=0, columnspan=4, sticky='nswe')
        
        dateFromLabel.grid(row=2, column=0, padx=(0, 5), pady=(10, 0), sticky='we')
        dateFromInput.grid(row=2, column=1, padx=5, pady=(10, 0), sticky='we')
        dateFromButton.grid(row=2, column=2, padx=5, pady=(10, 0), sticky='nswe')

        dateToLabel.grid(row=3, column=0, padx=(0, 10), pady=(10, 40), sticky='we')
        dateToInput.grid(row=3, column=1, padx=5, pady=(10, 40), sticky='we')
        dateToButton.grid(row=3, column=2, padx=5, pady=(10, 40), sticky='nswe')

        lastRunLabel.grid(row=2, column=3, rowspan=2, padx=5, pady=(10, 40), sticky='nswe')

        appleIdLabel.grid(row=4, column=0, padx=(0, 10), sticky='we')
        appleIdInput.grid(row=4, column=1, padx=5, sticky='we')
        eMailCmb.grid(row=4, column=2, padx=5, sticky='we')

        pwdLabel.grid(row=5, column=0, padx=(0, 10), pady=(10,0), sticky='we')
        pwdInput.grid(row=5, column=1, padx=5, pady=(10,0), sticky='we')
        pwdShow.grid(row=5, column=2, padx=5, pady=(10,0), sticky='we')

        startButton.grid(row=4, column=3, rowspan=2, padx=5, pady=10, sticky='nswe')
        self.console.grid(row=6, column=0, columnspan=4, padx=5, pady=10, sticky='nswe')

    def configure_grid_weights(self):
        for row in range(6):
            self.grid_rowconfigure(row, weight=1)
        for column in range(1, 4, 1):
            self.grid_columnconfigure(column,weight=1)
        self.grid_rowconfigure(6, weight=10)

    def show_hide_pass_clicked(self, checkbutton: tk.Checkbutton, pwdInput: tk.Entry, showPass: bool):
        if(showPass):
            pwdInput.config(show='')
            checkbutton['text'] = 'Hide password'
        else:
            pwdInput.config(show='*')
            checkbutton['text'] = 'Show password'

    def get_apple_id(self):
        appleIdInput = self.appleId.get()
        if appleIdInput.find('@') != -1: return appleIdInput
        email = self.email.get()
        return f'{appleIdInput}{email}'

    def start_import(self):
        # popUp = PopUpListBox(self, ['1', '2', '3'])

        if not self.validate_inputs(): return
        id, pwd, fromDate, toDate = self.get_apple_id(), self.pwd.get(), self.dateFrom.get(), self.dateTo.get()
        logic.load_photos(appleId=id, pwd=pwd, fromDate=fromDate, toDate=toDate, mainWindow=self)
        log.info('oh ye')

    def validate_inputs(self) -> bool:
        for input in self.inputs:
            if input.get().strip() == '':
                self.error['text'] = 'Please enter all the data'
                return False
            
        self.error['text'] = ''
        return True
    
    def pop_up_2fa(self):
        return simpledialog.askstring(
            title='2fa required', prompt='Enter the code from trusted device:')
    
    def pop_up_2sa(self, devices: list):
        popup = PopUpListBox(master=self, values=devices)
        popup.wait_window()