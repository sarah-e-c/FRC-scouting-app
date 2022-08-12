from PyQt6.QtWidgets import QLineEdit

class PlaygroundTextBox(QLineEdit):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
