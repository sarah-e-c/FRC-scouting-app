from PyQt6.QtWidgets import QMessageBox
import PyQt6.QtCore as core
class ErrorDialog():
    def __init__(self, window, main_message='Invalid Input', sub_message = 'Please input supported values.'):
        button = QMessageBox.critical(window, main_message, sub_message, buttons= QMessageBox.StandardButton.Ok)
        if button == QMessageBox.StandardButton.Ok:
            pass
class Constants:
    YEAR = 2022
    KEY = ''
    PRELOADED_DATA_FILEPATH = 'old code/data'
    APPLICATION_TITLE = 'ScoutingML'
    LATE_WEIGHTING = 2



