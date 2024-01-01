from gui.main_window import MainWindow
import logging as log

class Logger:
    def __init__(self, mainWindow: MainWindow):
        self.mainWindow = mainWindow
        self.configure_log()

    def configure_log(self):
        formatter = log.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        self.logger = log.getLogger()
        self.logger.propagate = False
        self.logger.setLevel(log.INFO)

        if not self.logger.hasHandlers():
            streamHandler = log.StreamHandler(self.mainWindow.console)
            streamHandler.setLevel(log.INFO)
            streamHandler.setFormatter(formatter)

            fileHandler = log.FileHandler('./log/log.log')
            fileHandler.setLevel(log.INFO)
            fileHandler.setFormatter(formatter)

            self.logger.addHandler(streamHandler)
            self.logger.addHandler(fileHandler)