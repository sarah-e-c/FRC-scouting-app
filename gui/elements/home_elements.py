from PyQt6.QtWidgets import QPushButton, QTabWidget

class HomeButton(QPushButton):
    def __init__(self, text, window, name, function):
        super(QPushButton, self).__init__(text, window)
        self.setBaseSize(100,100)
        self.name = name
        self.clicked.connect(lambda: function(window, self.name))

