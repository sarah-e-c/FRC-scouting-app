#PyQt6
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton,
                             QVBoxLayout, QLabel, QMenu, QHBoxLayout, QToolBar, QStatusBar, QTabWidget, QCheckBox,
                             QComboBox, QMessageBox, QDoubleSpinBox)
from PyQt6.QtCore import QSize, Qt
from PyQt6 import QtGui
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QRunnable, QThreadPool

# self-coded elements
from gui.elements.home_elements import HomeButton
from gui.elements.playground_elements import PlaygroundTextBox, PlaygroundWorker

# self-coded other things :)
from model_wrapper import FRCModel
from gui.utils import ErrorDialog, Constants

# general
import logging
import sys
import requests


# I had to hard code all of this because of lack of support :(


class Window(QMainWindow):
    """
    Main window class. Inherits from QMainWindow
    """

    def __init__(self):
        super().__init__()

        # making sure theres no funny business with the logger
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        format = logging.Formatter('%(process)d-%(levelname)s-%(name)s-%(message)s')

        # setting up file handler
        file_handler = logging.FileHandler(filename='logs.txt')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(format)
        self.logger.addHandler(file_handler)

        # setting up console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(format)
        self.logger.addHandler(console_handler)

        # aesthetics
        self.setWindowTitle(Constants.APPLICATION_TITLE)
        self.setWindowIcon(QIcon('gui/icons/home_icon.jpg'))
        self.setGeometry(100, 200, 1000, 700)

        # setting up toolbar
        toolbar = QToolBar('My main toolbar')
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        button_action = QAction(
            QIcon('gui/icons/home_icon.jpg'), 'Home button', self)
        button_action.setStatusTip('Return to home screen')
        button_action.triggered.connect(self.home_screen)
        toolbar.addAction(button_action)
        settings_action = QAction(
            QIcon('gui/icons/settings_icon.png'), 'Settings button', self)
        settings_action.setStatusTip('Configure settings')
        settings_action.triggered.connect(self.settings_screen)
        toolbar.addAction(settings_action)
        toolbar.toggleViewAction().setEnabled(False)

        self.setStatusBar(QStatusBar(self))
        self.threadpool = QThreadPool()

        self.mainWidget = QWidget()
        self.home_screen()

    def home_screen(self):
        """
        Function to set the window to the home screen.
        """
        self.mainWidget = QWidget()

        # handling
        def handle_home_buttons(window: Window, button_name: str) -> None:
            if button_name == '2022 Playground Button':
                window.playground_screen()

            if button_name == 'Upload Data Button':
                window.upload_data_screen()

            if button_name == 'Predict Sample Match Button':
                window.sample_match_prediction_screen()

            if button_name == 'Settings Button':
                window.settings_screen()

        outer_layout = QVBoxLayout()
        inner_layout = QHBoxLayout()

        self.home_buttons = {
            '2022 Playground Button': HomeButton('2022 Playground', self, '2022 Playground Button', handle_home_buttons),
            'Upload Data Button': HomeButton('Upload Data', self, 'Upload Data Button', handle_home_buttons),
            'Predict Sample Match Button': HomeButton('Predict Sample Match', self, 'Predict Sample Match Button', handle_home_buttons),
            'Settings Button': HomeButton('Settings', self, 'Settings Button', handle_home_buttons),
        }

        for _, button in self.home_buttons.items():
            inner_layout.addWidget(button)

        self.home_label = QLabel('Scouting Predictions v.0.01')
        self.home_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.addWidget(self.home_label)
        outer_layout.addLayout(inner_layout)
        self.mainWidget.setLayout(outer_layout)

        self.setCentralWidget(self.mainWidget)

    def playground_screen(self):
        """
        Function to set the window to the playground screen.
        """

        def run_playground_test(window: Window):
            window.playgroundOutputLabel.setText('Recieved input!')

            # parsing weeks
            if str(window.fit_selectors['weeks'].text()) == 'all':
                fit_weeks = [0, 1, 2, 3, 4, 5, -1]
            else:
                try:
                    fit_weeks = window.fit_selectors['weeks'].text().split(',')
                    for index, week in enumerate(fit_weeks):
                        fit_weeks[index] = int(week)
                except:
                    window.make_error_dialog()
                    return

            if str(window.predict_selectors['weeks'].text()) == 'all':
                predict_weeks = [0, 1, 2, 3, 4, 5, -1]
            else:
                try:
                    predict_weeks = window.predict_selectors['weeks'].text().split(
                        ',')
                    for index, week in enumerate(predict_weeks):
                        predict_weeks[index] = int(week)
                except:
                    window.make_error_dialog()
                    return
            
            late_weighting = self.lateWeightingSpinBox.value()
            #telling method to not use late weigting
            if late_weighting == 0.0:
                late_weighting = False
            
            worker = PlaygroundWorker(self.fitModeComboBox.currentText(), fit_weeks, predict_weeks, late_weighting)
            self.threadpool.start(worker)

            worker.signals.result.connect(self.playgroundOutputLabel.setText)
            self.playgroundRunButton.setEnabled(False)
            worker.signals.result.connect(lambda: self.playgroundRunButton.setEnabled(False))

            return
            # def thread_target():
            # model = FRCModel(mode=window.fitModeComboBox.currentText())
            # window.logger.debug('Started model fitting...')
            # model.fit(included_weeks=fit_weeks, data_preloaded_filepath=Constants.PRELOADED_DATA_FILEPATH)
            # window.playgroundOutputLabel.setText('Data fit!')
            # window.logger.debug('Finished model fitting, starting scoring...')

            # score = model.score(prediction_weeks=predict_weeks)
            # window.playgroundOutputLabel.setText(f'Accuracy: {score}')

            # thread = threading.Thread(target=thread_target)
            # thread.start()

        # setting up layout for selection
        selectionLayout = QVBoxLayout()

        fit_label = QLabel('Fit Matches')
        predict_label = QLabel('Predict Matches')

        self.fit_selectors = {
            'events': '',
            'districts': '',
            'weeks': ''
        }
        self.predict_selectors = {
            'events': '',
            'districts': '',
            'weeks': ''
        }

        selectionLayout.addWidget(fit_label)

        for name, _ in self.fit_selectors.items():
            mini_layout = QHBoxLayout()
            label = QLabel(name)
            textbox = PlaygroundTextBox(f'fit_{name}')
            mini_layout.addWidget(label)
            mini_layout.addWidget(textbox)
            self.fit_selectors[name] = textbox
            selectionLayout.addLayout(mini_layout)

        selectionLayout.addWidget(predict_label)

        for name, _ in self.predict_selectors.items():
            mini_layout = QHBoxLayout()
            label = QLabel(name)
            textbox = PlaygroundTextBox(f'predict_{name}')
            mini_layout.addWidget(label)
            mini_layout.addWidget(textbox)
            self.predict_selectors[name] = textbox
            selectionLayout.addLayout(mini_layout)

        settings_widget = QWidget()

        first_settings_page = QVBoxLayout()

        self.playground_toggles = {
            'Exclude Ties': '',
        }

        # drop down for fit modes
        self.fitModeComboBox = QComboBox()
        fit_modes = [
            'week_by_week',
            'default'
        ]
        self.fitModeComboBox.addItems(fit_modes)
        first_settings_page.addWidget(self.fitModeComboBox)

        # Late weighting spin box
        lateWeightingSpinBoxLabel = QLabel('Late Weighting')
        self.lateWeightingSpinBox = QDoubleSpinBox()
        self.lateWeightingSpinBox.setMinimum(0)
        self.lateWeightingSpinBox.setMaximum(10)
        self.lateWeightingSpinBox.setSingleStep(0.1)
        lateWeightingSpinBoxLayout = QHBoxLayout()
        lateWeightingSpinBoxLayout.addWidget(lateWeightingSpinBoxLabel)
        lateWeightingSpinBoxLayout.addWidget(self.lateWeightingSpinBox)
        first_settings_page.addLayout(lateWeightingSpinBoxLayout)

        for name, _ in self.playground_toggles.items():
            self.playground_toggles[name] = QCheckBox()
            mini_layout = QHBoxLayout()
            mini_layout.addWidget(QLabel(name))
            mini_layout.addWidget(self.playground_toggles[name])
            first_settings_page.addLayout(mini_layout)

        self.playgroundRunButton = QPushButton('Run test!')
        self.playgroundRunButton.clicked.connect(
            lambda: run_playground_test(self))
        first_settings_page.addWidget(self.playgroundRunButton)

        settings_widget.setLayout(first_settings_page)
        self.playgroundOutputLabel = QLabel('Statistics')
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.playgroundOutputLabel)
        right_layout.addWidget(settings_widget)

        outerLayout = QHBoxLayout()
        outerLayout.addLayout(selectionLayout)
        outerLayout.addLayout(right_layout)

        self.mainWidget = QWidget()  # resetting widget
        self.mainWidget.setLayout(outerLayout)
        self.setCentralWidget(self.mainWidget)

    def upload_data_screen(self):
        """
        Function to set the window to the upload data screen.
        """

        outerLayout = QHBoxLayout()
        file_upload_button = QPushButton('Upload data')
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(outerLayout)
        self.setCentralWidget(self.mainWidget)
        pass

    def sample_match_prediction_screen(self):
        """
        Function to set the window to the sample match prediction screen.
        """
        pass

    def settings_screen(self):
        """
        Function to set the window to the settings screen.
        """
        pass

    def make_error_dialog(self, message='An error occurred.', sub_message='Please try again.'):
        """
        Function to make an error dialogue
        """
        self.logger.debug('Error Dialog Created')
        ErrorDialog(self, main_message=message, sub_message=sub_message)
    # other UI control





app = QApplication(sys.argv)

window = Window()

window.show()

sys.exit(app.exec())
