
from decimal import InvalidOperation
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton,
QVBoxLayout, QLabel, QMenu, QHBoxLayout, QToolBar, QStatusBar, QTabWidget, QCheckBox,
QComboBox, QMessageBox)
from PyQt6.QtCore import QSize, Qt
import sys
from PyQt6 import QtGui
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QIcon

from gui.elements.home_elements import HomeButton
from gui.elements.playground_elements import PlaygroundTextBox

from model_wrapper import FRCModel
from gui.utils import ErrorDialog

# I had to hard code all of this because of lack of support :(
APPLICATION_TITLE = 'ScoutingML'
PRELOADED_DATA_FILEPATH = 'old code/data'

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # aesthetics
        self.setWindowTitle(APPLICATION_TITLE)
        self.setWindowIcon(QIcon('gui/icons/home_icon.jpg'))
        self.setGeometry(100,200,1000,700)

        # setting up toolbar
        toolbar = QToolBar('My main toolbar')
        toolbar.setIconSize(QSize(16,16))
        self.addToolBar(toolbar)
        button_action = QAction(QIcon('gui/icons/home_icon.jpg'), 'Home button', self)
        button_action.setStatusTip('Return to home screen')
        button_action.triggered.connect(self.home_screen)
        toolbar.addAction(button_action)
        toolbar.toggleViewAction().setEnabled(False)

        self.setStatusBar(QStatusBar(self))


        

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
            '2022 Playground Button': HomeButton('2022 Playground', self,'2022 Playground Button' , handle_home_buttons),
            'Upload Data Button': HomeButton('Upload Data', self,'Upload Data Button' , handle_home_buttons),
            'Predict Sample Match Button': HomeButton('Predict Sample Match', self,'Predict Sample Match Button' , handle_home_buttons),
            'Settings Button':HomeButton('Settings', self, 'Settings Button' , handle_home_buttons),
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
            window.playgroundOutputLabel.setText('Running test!')
            model = FRCModel(mode=self.fitModeComboBox.currentText())
            # parsing weeks
            if str(self.fit_selectors['weeks'].text()) == 'all':
                fit_weeks = [0,1,2,3,4,5,-1]
            else:
                ErrorDialog(self)
                return

            if str(self.predict_selectors['weeks'].text()) == 'all':
                predict_weeks = [0,1,2,3,4,5,-1]
            else:
                button = QMessageBox.critical(self, "Invalid input", 'Please input supported values.', buttons=QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.NoToAll | QMessageBox.StandardButton.Ignore,
                defaultButton=QMessageBox.StandardButton.Discard,)
                if button == QMessageBox.StandardButton.Discard:
                    print('hello!')

                if button == QMessageBox.StandardButton.Ok:
                    print("OK!")
                return
            

            model.fit(included_weeks=fit_weeks, data_preloaded_filepath=PRELOADED_DATA_FILEPATH)
            window.playgroundOutputLabel.setText('Data fit!')

            score = model.score(prediction_weeks=predict_weeks)
            window.playgroundOutputLabel.setText(f'Accuracy: {score}')
                        



        #setting up layout for selection
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

        for name, _ in self.playground_toggles.items():
            self.playground_toggles[name] = QCheckBox()
            mini_layout = QHBoxLayout()
            mini_layout.addWidget(QLabel(name))
            mini_layout.addWidget(self.playground_toggles[name])
            first_settings_page.addLayout(mini_layout)
        
        self.playgroundRunButton = QPushButton('Run test!')
        self.playgroundRunButton.clicked.connect(lambda: run_playground_test(self))
        first_settings_page.addWidget(self.playgroundRunButton)

        settings_widget.setLayout(first_settings_page)
        self.playgroundOutputLabel = QLabel('Statistics')
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.playgroundOutputLabel)
        right_layout.addWidget(settings_widget)


        outerLayout = QHBoxLayout()
        outerLayout.addLayout(selectionLayout)
        outerLayout.addLayout(right_layout)

        self.mainWidget = QWidget() # resetting widget
        self.mainWidget.setLayout(outerLayout)
        self.setCentralWidget(self.mainWidget)
        

    def upload_data_screen(self):
        """
        Function to set the window to the upload data screen.
        """
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


    # other UI control





app = QApplication(sys.argv)

window = Window()

window.show()

sys.exit(app.exec())