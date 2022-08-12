import pandas as pd
import numpy as np
import os

def team_stats_process(directory='teams_data'):
    """
    method that takes all of the teams data and compresses it into one file.
    directory='teams_data' -- folder that the team stats are in
    """

    
    team_paths = []

    for filename in os.scandir(directory):
        if filename.is_file():
            team_paths.append(filename.path)

    winrate_list = []
    hang_score_list = []
    team_auto_lower_list = []
    team_auto_upper_list = []
    team_tele_lower_list = []
    team_tele_upper_list = []
    total_team_points_list = []
    highest_comp_level_list = []
    team_name_list = []

    def get_winrate_highest_level(df):
        mapping = {'Yes': 1, 'Tie': 0.5, 'No': 0}
        winrate_list.append(df['WonGame'].map(mapping).mean())
        mapping_2 = {'None': 0, 'Low': 4, 'Mid': 8, 'High': 12, 'Traversal': 15}
        hang_score_list.append(df['Hang'].map(mapping_2).mean())
        team_auto_lower_list.append(df['TeamAutoLower'].mean())
        team_auto_upper_list.append(df['TeamAutoUpper'].mean())
        team_tele_lower_list.append(df['TeamTeleopLower'].mean())
        team_tele_upper_list.append(df['TeamTeleopUpper'].mean())
        mapping_3 = {'f': 5, 'sf': 3, 'qm': 0}
        highest_comp_level_list.append(df['comp_level'].map(mapping_3).max())

    for path in team_paths:
        df = pd.read_csv(path)
        team_name_list.append(path.split('/')[1].split('data')[0])
        get_winrate_highest_level(df)

    total_scores_df = pd.DataFrame({ 'TeamName': team_name_list,
                        'WinRate': winrate_list,
                        'TeamAutoLower': team_auto_lower_list,
                        'TeamAutoUpper': team_auto_upper_list,
                        'TeamTeleopLower': team_tele_lower_list,
                        'TeamTeleopUpper': team_tele_upper_list,
                        'HangScore': hang_score_list,
                        'HighestCompLevel': highest_comp_level_list
                        })

    total_scores_df.to_csv('all_team_stats.csv', index=False)
