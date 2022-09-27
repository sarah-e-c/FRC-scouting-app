from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
import logging
import pandas as pd
from data_handling import engine

from model_wrapper import FRCModel
import statistics

class SampleMatchTextBox(QLineEdit):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.setPlaceholderText('Enter team key, eg. frc422')

class SampleMatchWorker(QRunnable):
    """
    Worker object to handle the long-running task of running playground tasks
    """
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, red_team_1, red_team_2, red_team_3, blue_team_1, blue_team_2, blue_team_3, model):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.signals = SampleMatchWorkerSignals()
        self.red_team_1 = red_team_1
        self.red_team_2 = red_team_2
        self.red_team_3 = red_team_3
        self.blue_team_1 = blue_team_1
        self.blue_team_2 = blue_team_2
        self.blue_team_3 = blue_team_3
        self.model = model

    def run(self):
        self.logger.debug('Starting sample match...')
        stats_df = pd.read_sql('teams_profile_all_weeks', engine)
        
        

        def team_lookup_averages(team_list, team_stats_df):
            """
            Method to grab all of the team statistics of a given alliance and return the wanted meta stats
            team_list -- regular list of teams in an alliance
            team_stats_df -- pandas DataFrame with all teams' statistics
            """
            team_winrate_list = []
            team_auto_lower_list = []
            team_auto_upper_list = []
            team_teleop_lower_list = []
            team_teleop_upper_list = []
            team_hang_score_list = []
            team_highest_comp_level_list = []
            
            #iterating through teams and grabbing wanted stats
            for team in team_list:
                team_winrate_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['win_rate']))
                team_auto_lower_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['team_auto_lower']))
                team_auto_upper_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['team_auto_upper']))
                team_teleop_lower_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['team_teleop_lower']))
                team_teleop_upper_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['team_teleop_upper']))
                team_hang_score_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['hang_score']))
                team_highest_comp_level_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['highest_comp_level']))
            
            # returning the wanted meta statistics in a series (for a dataframe)
            return pd.Series({'avg_winrate': statistics.mean(team_winrate_list),
                                'highest_avg_winrate': max(team_winrate_list),
                                'lowest_avg_winrate': min(team_winrate_list),

                                'avg_auto_lower': statistics.mean(team_auto_lower_list),
                                'highest_auto_lower': max(team_auto_lower_list),

                                'avg_auto_upper': statistics.mean(team_auto_upper_list),
                                'highest_auto_upper': max(team_auto_upper_list),

                                'avg_teleop_lower': statistics.mean(team_teleop_lower_list),
                                'highest_teleop_lower': max(team_teleop_lower_list),

                                'avg_teleop_upper': statistics.mean(team_teleop_upper_list),
                                'highest_teleop_upper': max(team_teleop_upper_list),
                                'lowest_teleop_upper': min(team_teleop_upper_list),


                                'avg_hang_score': statistics.mean(team_hang_score_list),
                                'avg_highest_comp_level': statistics.mean(team_highest_comp_level_list),
                                })
        
        red_stats = team_lookup_averages([self.red_team_1, self.red_team_2, self.red_team_3], stats_df)
        blue_stats = team_lookup_averages([self.blue_team_1, self.blue_team_2, self.blue_team_3], stats_df)
        total_stats = red_stats - blue_stats
        raw_num = self.model.predict(pd.DataFrame([total_stats]))
        mapping = {0: 'Blue', 1:'Tie', 2: 'Red'}
        self.logger.debug(f'{mapping[raw_num[0]]} wins!')
        self.signals.result.emit(f'{mapping[raw_num[0]]} wins!')
        self.signals.finished.emit()

class SampleMatchWorkerSignals(QObject):
    result = pyqtSignal(object)
    finished = pyqtSignal()

if __name__ == '__main__':
    model = FRCModel('XGBoost', 'week_by_week', 1.5)
    model.fit(fit_weeks='all')
    worker = SampleMatchWorker('frc422', 'frc422', 'frc422', 'frc1086', 'frc1086', 'frc1086', 'frc1086', FRCModel('XGBoost', 'week_by_week', 1.5))