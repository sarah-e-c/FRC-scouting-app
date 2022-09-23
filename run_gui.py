#PyQt6

from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton,
                             QVBoxLayout, QLabel, QMenu, QHBoxLayout, QToolBar, QStatusBar, QTabWidget, QCheckBox,
                             QComboBox, QMessageBox, QDoubleSpinBox, QFileDialog, QTextEdit)
from PyQt6.QtCore import QSize, Qt
from PyQt6 import QtGui
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThreadPool

# self-coded elements
from gui.elements.home_elements import HomeButton
from gui.elements.playground_elements import PlaygroundTextBox, PlaygroundWorker
from gui.elements.sample_match_test_elements import SampleMatchTextBox, SampleMatchWorker
from gui.elements.settings_screen_elements import ImplementSettingsWorker
from gui.elements.data_workers import PingerWorker, DictionaryDataWorker, TBADataWorker, UserDataWorker, EventsDataWorker

# self-coded other things :)
from model_wrapper import FRCModel
from utils import ErrorDialog, Constants
import secrets
import first_time_setup
import data_handling

# general
import logging
import sys
import requests
import configparser
import os


logging.basicConfig(level=logging.DEBUG)
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
        self.logger = logging.getLogger()
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

        # making sure that data is loaded in -- if not, then run first time setup
        if not os.path.isfile('data.db'):
            first_time_setup.setup_application()

        
        #setting up defult model for fun testing and such
        self.settings_config = configparser.ConfigParser()
        self.settings_config.read('config.ini')
        try:
            self.model_config = self.settings_config['model']
        except Exception as e:
            self.logger.warn(e, 'application is not set up yet.')
            # setting up the ini file -- probably reshape this a little bit
        try:
            self.FRCmodel = FRCModel(mode=self.settings_config['model']['mode'], model=self.settings_config['model']['type'], late_weighting=self.model_config.getfloat('late_weighting'), enable_sql=True)
            self.FRCmodel.fit(included_weeks=self.settings_config['model']['included_weeks'], data_preloaded_filepath=True, matches_data_preloaded_filepath=True, write_data=True)
        except Exception as e:
            self.logger.exception(e)
            raise e

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
                # setting up pinger
        pinger = PingerWorker()
        self.threadpool.start(pinger)

        pinger.signals.needs_update_signal.connect(self.update_notification)
        pinger.signals.needs_tba_data_signal.connect(self.get_new_tba_data)
        pinger.signals.needs_dictionary_data_signal.connect(self.get_new_dictionary_data)
        pinger.signals.needs_user_submitted_data_signal.connect(self.get_new_user_submitted_data)
        pinger.signals.needs_event_data_signal.connect(self.get_new_events_data)
        pinger.signals.disconnected_signal.connect(self.notify_disconnect)
        pinger.signals.reconnected_signal.connect(self.notify_reconnect)

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
        tooltips = [
            'Experiment and test model accuracy on 2022 data.',
            'Support the project by uploading data to the api.',
            'See who would win in a fake match. Any team, any district!',
            'Configure settings.'
        ]

        for tooltip, button in zip(tooltips, self.home_buttons.items()):
            button[1].setStatusTip(tooltip)
            inner_layout.addWidget(button[1])
        
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

        
        def file_upload(data):
            try:
                requests.post(Constants.SERVER_URL, data)
            except Exception as e:
                self.logger.warning(f'Error connecting to application server. {e}')
        outerLayout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit_text = """
        Upload data to the application api. Helps imporve predictions! \n
        Guidelines: Our api takes input data in both flat json and csv formats. \n
        Required columns:
        team_name -- also acceptable 'teamName' or 'team_number' or 'teamNumber': The team that the scouter was focuesed on.
        match_key (matchKey) \n
        OR \n
        match_number also acceptable matchNumber AND event_key also acceptable eventKey (unique identifier for event) \n
        These allow us to match the scouted data to TBA data. \n
        Suggested columns: \n
        team_auto_upper_cargo -- also acceptable teamAutoUpperCargo: the amount of balls that the team scored in the upper goal during autonomous. \n
        team_auto_lower_cargo -- also acceptable teamAutoLowerCargo: the amount of balls that the team scored in the lower goal during autonomous. \n
        team_teleop_upper_cargo -- also acceptable teamTeleopUpperCargo: the amount of balls that the team scored in the upper goal during teleop.\n
        team_teleop_lower_cargo -- also acceptable teamTeleopLowerCargo: the amount of balls that the team scored in the lower goal during teleop. \n
        """
        text_edit.setText(text_edit_text)
        text_edit.setReadOnly(True)
        outerLayout.addWidget(text_edit)
        file_upload_button = QPushButton('Upload data')
        file_dialog = QFileDialog()
        def file_dialog_get(window: Window):
            #wrong
            data = file_dialog.getOpenFileName(window, "Upload Data", 'Downloads', "Data Files (*.json, *.csv)")
            file_upload(data)
        file_upload_button.pressed.connect(lambda: file_dialog_get(self))
        file_upload_button.setStatusTip('Select data to upload!')
        outerLayout.addWidget(file_upload_button)
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(outerLayout)
        self.setCentralWidget(self.mainWidget)
        

    def sample_match_prediction_screen(self):
        """
        Function to set the window to the sample match prediction screen.
        """
        def run_sample_match_test(window: Window):
            window.sample_match_output_textbox.setText('Recieved input!')

            # parsing weeks
            try:
                red_team_1 = window.red_selectors['team 1'].text()
                red_team_2 = window.red_selectors['team 2'].text()
                red_team_3 = window.red_selectors['team 3'].text()
                blue_team_1 = window.blue_selectors['team 1'].text()
                blue_team_2 = window.blue_selectors['team 2'].text()
                blue_team_3 = window.blue_selectors['team 3'].text()
            except Exception as e:
                self.logger.debug(f'rejected user input from sample match data {e}')
                window.make_error_dialog()
                return
        
            
            worker = SampleMatchWorker(red_team_1, red_team_2, red_team_3, blue_team_1, blue_team_2, blue_team_3, self.FRCmodel)
            self.threadpool.start(worker)

            worker.signals.result.connect(self.sample_match_output_textbox.setText)
            self.sample_match_run_button.setEnabled(False)
            worker.signals.finished.connect(lambda: self.sample_match_run_button.setEnabled(True))

        selectionLayout = QVBoxLayout()

        red_label = QLabel('Red Alliance')
        blue_label = QLabel('Blue Alliance')

        self.red_selectors = {
            'team 1': '',
            'team 2': '',
            'team 3': ''
        }
        self.blue_selectors = {
            'team 1': '',
            'team 2': '',
            'team 3': ''
        }

        selectionLayout.addWidget(red_label)

        for name, _ in self.red_selectors.items():
            mini_layout = QHBoxLayout()
            label = QLabel(name)
            textbox = SampleMatchTextBox(f'red_{name}')
            mini_layout.addWidget(label)
            mini_layout.addWidget(textbox)
            self.red_selectors[name] = textbox
            selectionLayout.addLayout(mini_layout)
        
        selectionLayout.addWidget(blue_label)
        for name, _ in self.blue_selectors.items():
            mini_layout = QHBoxLayout()
            label = QLabel(name)
            textbox = SampleMatchTextBox(f'blue_{name}')
            mini_layout.addWidget(label)
            mini_layout.addWidget(textbox)
            self.blue_selectors[name] = textbox
            selectionLayout.addLayout(mini_layout)
        
        outerLayout = QHBoxLayout()
        outerLayout.addLayout(selectionLayout)
        
        outputLayout = QVBoxLayout()
        
        self.sample_match_output_textbox = QTextEdit()
        self.sample_match_output_textbox.setReadOnly(True)
        outputLayout.addWidget(self.sample_match_output_textbox)

        self.sample_match_run_button = QPushButton('Run test!')
        self.sample_match_run_button.pressed.connect(lambda: run_sample_match_test(self))
        outputLayout.addWidget(self.sample_match_run_button)
        
        outerLayout.addLayout(outputLayout)

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(outerLayout)
        
        self.setCentralWidget(self.mainWidget)
        self.logger.debug('Sample match predict screen loaded')
        

    def settings_screen(self):
        """
        Function to set the window to the settings screen.
        """
        

        def change_settings():
            if self.modelLateWeightingSpinBox.value() < 0.05:
                self.settings_config['model']['late_weighting'] = '0.0'
            else:
                self.settings_config['model']['late_weighting'] = str(self.modelLateWeightingSpinBox.value())
            
            self.settings_config['model']['mode'] = self.modelFitModeComboBox.currentText()
            self.settings_config['model']['type'] = self.modelTypeComboBox.currentText()

            # still need to configure included weeks
            self.settings_config['model']['included_weeks'] = 'all'

            with open('config.ini', 'w') as configfile:
                self.settings_config.write(configfile)
            self.logger.debug('Settings changed.')
            worker = ImplementSettingsWorker(self.settings_config['model']['type'], self.settings_config['model']['type'], self.model_config.getfloat('late_weighting'))

            worker.signals.result.connect(self.changeSettingsOutput.setText)

            self.changeSettingsButton.setEnabled(False)
            def change_model(new_model):
                self.FRCmodel = new_model
            
            worker.signals.model.connect(change_model)
            worker.signals.finished.connect(lambda: self.changeSettingsButton.setEnabled(True))
            self.threadpool.start(worker)


        model_settings_label = QLabel('Configure default model')
        
        model_type_label = QLabel('Model type')
        self.modelTypeComboBox = QComboBox()
        self.modelTypeComboBox.addItem('XGBoost')
        self.modelTypeComboBox.addItem('Winrate Comparison (not yet supported)')
        self.modelTypeComboBox.addItem('Random Forest (not yet supported)')
        self.modelTypeComboBox.addItem('Logistic Regression (not yet supported)')
        self.modelTypeComboBox.setCurrentText(self.model_config['type'])

        model_type_layout = QHBoxLayout()
        model_type_layout.addWidget(model_type_label)
        model_type_layout.addWidget(self.modelTypeComboBox)

        first_settings_layout = QVBoxLayout()
        first_settings_layout.addWidget(model_settings_label)
        first_settings_layout.addLayout(model_type_layout)
        
        model_fit_mode_label = QLabel('Model fit mode')
        self.modelFitModeComboBox = QComboBox()
        self.modelFitModeComboBox.addItem('week_by_week')
        self.modelFitModeComboBox.addItem('full_comparison')
        self.modelFitModeComboBox.setCurrentText(self.model_config['mode'])

        model_fit_mode_layout = QHBoxLayout()
        model_fit_mode_layout.addWidget(model_fit_mode_label)
        model_fit_mode_layout.addWidget(self.modelFitModeComboBox)


        first_settings_layout.addLayout(model_fit_mode_layout)

        model_late_weighting_label = QLabel('Model late weighting')
        self.modelLateWeightingSpinBox = QDoubleSpinBox()
        self.modelLateWeightingSpinBox.setMinimum(0.0)
        self.modelLateWeightingSpinBox.setMaximum(10.0)
        self.modelLateWeightingSpinBox.setSingleStep(0.1)
        self.modelLateWeightingSpinBox.setValue(self.model_config.getfloat('late_weighting'))

        model_late_weighting_layout = QHBoxLayout()
        model_late_weighting_layout.addWidget(model_late_weighting_label)
        model_late_weighting_layout.addWidget(self.modelLateWeightingSpinBox)

        first_settings_layout.addLayout(model_late_weighting_layout)

        output_and_button_layout = QVBoxLayout()
        self.changeSettingsOutput = QTextEdit()
        self.changeSettingsOutput.setReadOnly(True)
        self.changeSettingsOutput.setText('Confirm Settings?')
        output_and_button_layout.addWidget(self.changeSettingsOutput)
        self.changeSettingsButton = QPushButton('Confirm Settings')
        self.changeSettingsButton.pressed.connect(change_settings)
        output_and_button_layout.addWidget(self.changeSettingsButton)

        outerLayout = QHBoxLayout()

        outerLayout.addLayout(first_settings_layout)
        outerLayout.addLayout(output_and_button_layout)
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(outerLayout)
        
        self.setCentralWidget(self.mainWidget)
        self.logger.debug('Settings screen loaded')

    def make_error_dialog(self, message='An error occurred.', sub_message='Please try again.'):
        """
        Function to make an error dialogue.
        message='An error occurred' - message that appears in the title bar (invisible on macos)
        sub_message = 'Please try again' - message that appears on the screen.
        """
        self.logger.debug('Error Dialog Created')
        ErrorDialog(self, main_message=message, sub_message=sub_message)
    
    def update_notification(self):
        """
        makes a popup error notification
        """
        self.make_error_dialog(message='An update is available.', sub_message='An update is available. Please download the new version.')

    def get_new_dictionary_data(self):
        """
        Starts a thread to get the new dictionary data from the api
        """
        worker = DictionaryDataWorker() # can connect a finsihed signal to something
        self.threadpool.start(worker)

    def get_new_tba_data(self):
        """
        Starts a thread to get the new Blue Alliance data from the api
        """
        worker = TBADataWorker() # can connect a finsihed signal to something
        self.threadpool.start(worker)


    def get_new_events_data(self):
        """
        Starts a thread to get the new events data from the api
        """
        worker = EventsDataWorker() # can connect a finsihed signal to something
        self.threadpool.start(worker)

    def get_new_user_submitted_data(self):
        """
        Starts a thread to get user submitted data from the api
        """
        worker = UserDataWorker() # can connect a finsihed signal to something
        self.threadpool.start(worker)

    def notify_disconnect(self):
        pass
    def notify_reconnect(self):
        pass

# run window

app = QApplication(sys.argv)

window = Window()

window.show()

sys.exit(app.exec())
