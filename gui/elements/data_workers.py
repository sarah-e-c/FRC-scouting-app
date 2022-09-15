from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
import requests
import time
from gui.utils import Constants
import configparser
import logging
from data_handling import grabber

HEADER = {'Auth Key': '1234',
            'CurrentVersion': Constants.VERSION,
            'VersionTBAData': 0,
            'VersionDictionaryData': 0,
            'VersionUserSubmittedData': 0} # TODO


config = configparser.ConfigParser()
config.read('config.ini')
logger = logging.getLogger(__name__)

class PingerWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = PingerSignals()

    def run(self):
        exception_counter = 0
        disconnected = False
        while True:
            if exception_counter == 40: 
                self.autoDelete()

            response = requests.get(f"{Constants.API_ENDPOINT}/ping", HEADER)
            try: 
                if response.headers['NewVersion'] == 'True':
                    self.signals.needs_update_signal.emit()
                if response.headers['NewTBAData'] == 'True':
                    self.signals.needs_tba_data_signal.emit()
                if response.headers['NewDictionaryData'] == 'True':
                    self.signals.needs_dictionary_data_signal.emit()
                if response.headers['NewUserSubmittedData'] == 'True':
                    self.signals.needs_user_submitted_data_signal.emit()
                if response.headers['NewEventsData'] == 'True':
                    self.signals.needs_event_data_signal.emit()
                if disconnected:
                    disconnected = False # I know this is bad im sorry
                    self.signals.reconnected_signal.emit()
                    exception_counter = 0

            except Exception as e:
                logger.warning(e)
                disconnected = True
                self.signals.disconnected_signal.emit()
                exception_counter += 1

            time.sleep(5)
    

class PingerSignals(QObject):
    needs_update_signal = pyqtSignal()
    needs_tba_data_signal = pyqtSignal()
    needs_dictionary_data_signal = pyqtSignal()
    needs_user_submitted_data_signal = pyqtSignal()
    needs_event_data_signal = pyqtSignal()
    disconnected_signal = pyqtSignal()
    reconnected_signal = pyqtSignal()


class DictionaryDataWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = DataWorkerSignals()
    
    def run(self):
        grabber.get_match_dictionary()
        self.signals.finished_signal.emit()

class DataWorkerSignals(QObject):
    finished_signal = pyqtSignal()

class EventsDataWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = DataWorkerSignals()
    
    def run(self):
        grabber.get_events_data()
        self.signals.finished_signal.emit()

class TBADataWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = DataWorkerSignals()
    
    def run(self):
        grabber.get_expanded_match_data()
        self.signals.finished_signal.emit()

class UserDataWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = DataWorkerSignals()
    
    def run(self):
        grabber.get_user_submitted_data()
        self.signals.finsihed_signal.emit()
