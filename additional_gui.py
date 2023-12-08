from tkinter.scrolledtext import ScrolledText 
import tkinter as tk 

import logic

class TkConsole(ScrolledText):
    def write(self, text:str):
        self.insert(index='end', chars=text)
    def flush(self):
        pass

class PopUpListBox(tk.Toplevel):
    def __init__(self, master, values: list):
        # Initialize popup
        tk.Toplevel.__init__(self=self, master=master)
        self.title = 'Two step authentication'

        # Label
        label = tk.Label( 
            master=self, justify='left',
            text='Please choose trusted device from a list\nbelow to use for authentification'
        )
        
        # List of trusted devices
        listVar = tk.Variable(master=self, value=values)
        self.listbox = tk.Listbox(
            master=self, listvariable=listVar, selectmode='single',
            selectbackground='Gray', activestyle='none')

        # End choice button
        button = tk.Button(master=self, text='Choose device', 
                           bg='blue', fg='white', font='Bauhaus 18 bold',
                           command=self.exit_pop)

        # Grid the elements
        label.grid(row=0, column=0, padx=5, pady=5, sticky='nswe')
        self.listbox.grid(row=1, column=0, padx=5, pady=(0,5), sticky='nswe')
        button.grid(row=2, column=0, padx=5, pady=(0,5), sticky='nswe')

    def exit_pop(self):
        logic.device = self.listbox.get(self.listbox.curselection())
        self.destroy()