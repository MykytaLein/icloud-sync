from main_window    import MainWindow
from logger         import Logger
from tkinter        import Tk

def main():
    root = Tk()
    root.option_add("*Font", "Bauhaus")
    mainWindow = MainWindow(master=root)
    logger = Logger(mainWindow)
    
    root.grid_columnconfigure(0,weight=1)
    root.grid_rowconfigure(0,weight=1)
    root.minsize(width=700, height=295)

    mainWindow.grid(row=0, column=0, padx=10, pady=10, sticky='nswe')
    root.mainloop()

if __name__ == '__main__':
    main()