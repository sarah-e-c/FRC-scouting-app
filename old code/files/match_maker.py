import pandas as pd
import requests
import time
import statistics


def load_matches():
    def team_lookup_averages(team_list, df_teams):
        team_winrate_list = []
        team_auto_lower_list = []
        team_auto_upper_list = []
        team_teleop_lower_list = []
        team_teleop_upper_list = []
        team_hang_score_list = []
        team_highest_comp_level_list = []
        
        for team in team_list:
            team_winrate_list.append(float(df_teams.loc[df_teams['TeamName'] == team]['WinRate']))
            team_auto_lower_list.append(float(df_teams.loc[df_teams['TeamName'] == team]['TeamAutoLower']))
            team_auto_upper_list.append(float(df_teams.loc[df_teams['TeamName'] == team]['TeamAutoUpper']))
            team_teleop_lower_list.append(float(df_teams.loc[df_teams['TeamName'] == team]['TeamTeleopLower']))
            team_teleop_upper_list.append(float(df_teams.loc[df_teams['TeamName'] == team]['TeamTeleopUpper']))
            team_hang_score_list.append(float(df_teams.loc[df_teams['TeamName'] == team]['HangScore']))
            team_highest_comp_level_list.append(float(df_teams.loc[df_teams['TeamName'] == team]['HighestCompLevel']))
        
        return pd.Series({'AvgWinrate': statistics.mean(team_winrate_list),
                            'HighestAvgWinrate': max(team_winrate_list),
                            'LowestAvgWinrate': min(team_winrate_list),

                            'AvgAutoLower': statistics.mean(team_auto_lower_list),
                            'HighestAutoLower': max(team_auto_lower_list),

                            'AvgAutoUpper': statistics.mean(team_auto_upper_list),
                            'HighestAutoUpper': max(team_auto_upper_list),

                            'AvgTeleopLower': statistics.mean(team_teleop_lower_list),
                            'HighestTelopLower': max(team_teleop_lower_list),

                            'AvgTelopUpper': statistics.mean(team_teleop_upper_list),
                            'HighestTelopUpper': max(team_teleop_upper_list),
                            'LowestTelopUpper': min(team_teleop_upper_list),


                            'AvgHangScore': statistics.mean(team_hang_score_list),

                            'AvgHighestCompLevel': statistics.mean(team_highest_comp_level_list),


                            })

    def get_teams(df):
        red_teams_list = []
        blue_teams_list = []
        for i in range(df.shape[0]):
            red_teams_list.append(df.iloc[i]['alliances']['red']['team_keys'])
            blue_teams_list.append(df.iloc[i]['alliances']['blue']['team_keys'])
        return pd.DataFrame({'Red': red_teams_list, 'Blue': blue_teams_list})

    def get_team_averages(team_list_df, df_team_info):
        series_list = []
        for i in range(team_list_df.shape[0]):
            team_info_red = team_lookup_averages(team_list_df.iloc[i]['Red'], df_team_info).rename('Red Averages')
            team_info_blue = team_lookup_averages(team_list_df.iloc[i]['Blue'], df_team_info).rename('Blue Averages')
            series_list.append(team_info_red - team_info_blue)
        
        return pd.DataFrame(series_list)

    def clean_data(match_data, team_stats_df):
        teams_list = get_teams(match_data)
        winner_series = match_data['winning_alliance'].map({'red': 1, '': 0, 'blue': -1})
        return get_team_averages(teams_list, team_stats_df).join(winner_series)


    team_stats_df = pd.read_csv('all_team_stats.csv')

    event_keys = [
    "2022va305",
    '2022va306',
    '2022va319',
    "2022va320",
    '2022dc305',
    '2022dc306',
    '2022dc312',
    '2022dc313',
    '2022dc326'
    ]

    header = {'X-TBA-Auth-Key': 'j5psodzpSE2HyqjKqVQUfC35jmvDo8Cb0YFHZN6ky76Arm4rQ7H2xD370QSwEmsC'}

    matches_data_list = []
    for event in event_keys:
        source = requests.get(f'https://www.thebluealliance.com/api/v3/event/{event}/matches', header).text
        matches_data_list.append(pd.read_json(source))
        time.sleep(1)

    all_matches_data = []
    for match in matches_data_list:
        all_matches_data.append(clean_data(match, team_stats_df))

    all_matches_df = pd.concat(all_matches_data)

    all_matches_df.to_csv('all_matches_stats.csv')
