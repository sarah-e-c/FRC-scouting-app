from PyQt6.QtCore import QRunnable, QObject, pyqtSignal

from model_wrapper import FRCModel
import logging

logger = logging.getLogger(__name__)

class ImplementSettingsWorker(QRunnable):
    def __init__(self, model_type, model_fit_mode, late_weighting):
        super().__init__()
        self.model_type = model_type
        self.model_fit_mode = model_fit_mode
        self.late_weighting = late_weighting
        self.included_weeks = 'all'
        self.signals = ImplementSettingsWorkerSignals()

    def run(self):
        logger.debug('process running...')
        FRCmodel = FRCModel(mode=self.model_fit_mode, model=self.model_type, late_weighting=self.late_weighting)
        self.signals.result.emit('Made model, starting fitting...')
        FRCmodel.fit(included_weeks=self.included_weeks, data_preloaded_filepath='old code/data', write_data=False)

        self.signals.result.emit('Finished fitting, all done!')
        self.signals.model.emit(FRCmodel)
        logger.debug('Finsihed fitting')
        self.signals.finished.emit()

class ImplementSettingsWorkerSignals(QObject):
        result = pyqtSignal(object)
        model = pyqtSignal(object)
        finished = pyqtSignal()
