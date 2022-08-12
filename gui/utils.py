from PyQt6.QtWidgets import QMessageBox
import PyQt6.QtCore as core
class ErrorDialog():
    def __init__(self, window):
        button = QMessageBox.critical(window, "Invalid input", 'Please input supported values.', buttons=QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.NoToAll | QMessageBox.StandardButton.Ignore,
        defaultButton=QMessageBox.StandardButton.Discard,)
        if button == QMessageBox.StandardButton.Discard:
            print('hello!')
        if button == QMessageBox.StandardButton.Ok:
            print("OK!")

class Constants:
    YEAR = 2022
    KEY = ''


