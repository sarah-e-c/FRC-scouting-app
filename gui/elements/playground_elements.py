from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
import logging
from gui.utils import Constants

from model_wrapper import FRCModel


class PlaygroundTextBox(QLineEdit):
    def __init__(self, name):
        super().__init__()
        self.name = name
        if (name == 'fit_weeks') | (name == 'predict_weeks'):
            self.setPlaceholderText('Enter all or enter integers separated by commas. Ex. 2,3,4,-1')
        else:
            self.setPlaceholderText('Not currently supported.')


class PlaygroundWorker(QRunnable):
    """
    Worker object to handle the long-running task of running playground tasks
    """
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, mode, fit_weeks, predict_weeks, late_weighting):
        super().__init__()

        # logging
        self.logger = logging.getLogger(__name__)
        


        self.mode = mode
        self.fit_weeks = fit_weeks
        self.predict_weeks = predict_weeks
        self.late_weighting = late_weighting
        self.signals = PlaygroundWorkerSignals()

    def run(self):
        model = FRCModel(mode=self.mode, late_weighting=self.late_weighting)
        self.logger.debug('Started model fitting...')
        model.fit(included_weeks=self.fit_weeks,
                  data_preloaded_filepath=Constants.PRELOADED_DATA_FILEPATH)
        self.logger.debug('Finished model fitting, starting scoring...')
        self.signals.result.emit('Finished model fitting, starting scoring...')
        score = model.score(prediction_weeks=self.predict_weeks)
        self.signals.result.emit(f'Accuracy: {score}')
        self.signals.finished.emit()

class PlaygroundWorkerSignals(QObject):
    result = pyqtSignal(object)
    finished = pyqtSignal()
