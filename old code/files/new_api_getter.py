# this is a file that is a bit better! 
import pandas as pd
import requests
import time
import numpy as np

#must send key with header (please dont steal my key  :()
header = {'X-TBA-Auth-Key': 'j5psodzpSE2HyqjKqVQUfC35jmvDo8Cb0YFHZN6ky76Arm4rQ7H2xD370QSwEmsC'}


def get_api_data():
    def get_score_data(df, team_name):

        taxied_list = []
        endgames_list = []

        auto_lower_points_list = []
        auto_upper_points_list = []
        tele_lower_points_list = []
        tele_upper_points_list = []

        total_team_points_list = []
        won_game_list = []


        # iterating through all:
        for i in range(df.shape[0]):
            team_alliance = df.iloc[i]['team_alliance']
            try:
                data_list = df.iloc[i]['score_breakdown'][team_alliance]
                # which robot were they ?
                if df.iloc[i]['Teammate1'] == team_name:
                    taxied_list.append(data_list['taxiRobot1'])
                    endgames_list.append(data_list['endgameRobot1'])
                if df.iloc[i]['Teammate2'] == team_name:
                    taxied_list.append(data_list['taxiRobot2'])
                    endgames_list.append(data_list['endgameRobot2'])
                if df.iloc[i]['Teammate3'] == team_name:
                    taxied_list.append(data_list['taxiRobot3'])
                    endgames_list.append(data_list['endgameRobot3'])
            except:
                taxied_list.append(None)
                endgames_list.append(None)
            
            try:
                # auto lower
                total_auto_lower_points = (data_list['autoCargoLowerBlue'] +  data_list['autoCargoLowerFar']
                                            + data_list['autoCargoLowerNear'] + data_list['autoCargoLowerRed'])
                auto_lower_points_list.append(total_auto_lower_points)
            except:
                auto_lower_points_list.append(None)
            
            try:
                # auto upper
                total_auto_upper_points = (data_list['autoCargoUpperBlue'] +  data_list['autoCargoUpperFar']
                                            + data_list['autoCargoUpperNear'] + data_list['autoCargoUpperRed'])
                auto_upper_points_list.append(total_auto_upper_points)
            
            except:
                auto_upper_points_list.append(None)
            
            try:
                # teleop lower
                total_teleop_lower_points = (data_list['teleopCargoLowerBlue'] +  data_list['teleopCargoLowerFar']
                                            + data_list['teleopCargoLowerNear'] + data_list['teleopCargoLowerRed'])    
                tele_lower_points_list.append(total_teleop_lower_points)
            
            except:
                tele_lower_points_list.append(None)
            
            try:
                # teleop upper
                total_teleop_upper_points = (data_list['teleopCargoUpperBlue'] +  data_list['teleopCargoUpperFar']
                                            + data_list['teleopCargoUpperNear'] + data_list['teleopCargoUpperRed'])    
                tele_upper_points_list.append(total_teleop_upper_points)
            
            except:
                tele_upper_points_list.append(None)
            
            # won game ?
            total_team_points_list.append(data_list['totalPoints'])
            if df.iloc[i]['team_alliance'] == df.iloc[i]['winning_alliance']:
                won_game_list.append('Yes')
            elif df.iloc[i]['winning_alliance'] == '': # checking if its nan
                won_game_list.append('Tie')
            else:
                won_game_list.append('No')


        return pd.DataFrame({'Taxied': taxied_list,
                            'Hang': endgames_list,
                            'TeamAutoLower': auto_lower_points_list,
                            'TeamAutoUpper': auto_upper_points_list,
                            'TeamTeleopLower': tele_lower_points_list,
                            'TeamTeleopUpper': tele_upper_points_list,
                            'TotalTeamPoints': total_team_points_list,
                            'WonGame': won_game_list
        }) 


    def get_team(df, team_name):
        team_list = []
        for i in range(df.shape[0]):
            #team_split_string = df.iloc[i]['alliances'].split('red')
            try:
                if team_name in df.iloc[i]['alliances']['blue']['team_keys']:
                    team_list.append('blue')
                elif team_name in df.iloc[i]['alliances']['red']['team_keys']:
                    team_list.append('red')
                else:
                    print('Warning: Team name not found')
            except:
                team_list.append('red')
        return pd.Series(team_list, name='team_alliance')


    # returns dataframe of opponents and teammates
    def get_opponents(df):
        teammate_1_list = []
        teammate_2_list = []
        teammate_3_list = []

        opponent_1_list = []
        opponent_2_list = []
        opponent_3_list = []

        for i in range(df.shape[0]):
            if df.iloc[i]['team_alliance'] == 'red':
                teammate_list = df.iloc[i]['alliances']['red']['team_keys']
                teammate_1_list.append(teammate_list[0])
                teammate_2_list.append(teammate_list[1])
                teammate_3_list.append(teammate_list[2])
                opponent_list = df.iloc[i]['alliances']['blue']['team_keys']
                opponent_1_list.append(opponent_list[0])
                opponent_2_list.append(opponent_list[1])
                opponent_3_list.append(opponent_list[2])
            else:
                teammate_list = df.iloc[i]['alliances']['blue']['team_keys']
                teammate_1_list.append(teammate_list[0])
                teammate_2_list.append(teammate_list[1])
                teammate_3_list.append(teammate_list[2])
                opponent_list = df.iloc[i]['alliances']['red']['team_keys']
                opponent_1_list.append(opponent_list[0])
                opponent_2_list.append(opponent_list[1])
                opponent_3_list.append(opponent_list[2])
        
        return pd.DataFrame({'Teammate1': teammate_1_list,
                            'Teammate2': teammate_2_list, 
                            'Teammate3': teammate_3_list,
                            'Opponent1': opponent_1_list,
                            'Opponent2': opponent_2_list,
                            'Opponent3': opponent_3_list
                            })

    def load_data(good_event_list):
        all_teams_matches = {}
        all_matches = []
        all_teams = [] # getting all teams

        # #getting all matches from all events
        # for event in good_event_list:
        #     event_matches = pd.read_json(requests.get(f'https://www.thebluealliance.com/api/v3//event/{event}/matches', header).text)
        #     all_matches.append(event_matches)
        #     time.sleep(0.3) # being nice
        
        # # writing this to a csv so less requests
        # print('done requesting!')

        # all_matches = pd.concat(all_matches)

        # all_matches.to_csv('all_matches_uncleaned.csv', index=False)

        all_matches = pd.read_csv('all_matches_uncleaned.csv')
        all_matches = all_matches.loc[all_matches['event_key'].apply(lambda x: x in good_event_list)]

        all_matches['alliances'] = all_matches['alliances'].map(eval)
        all_matches['score_breakdown'] = all_matches['score_breakdown'].map(eval)
        # print('written to csv!!!')
        for match in all_matches['alliances']:

            # getting a list of teams
            all_teams.append(match['red']['team_keys'][0])
            all_teams.append(match['red']['team_keys'][1])
            all_teams.append(match['red']['team_keys'][2])
            all_teams.append(match['blue']['team_keys'][0])
            all_teams.append(match['blue']['team_keys'][1])
            all_teams.append(match['blue']['team_keys'][2])
            
        # getting rid of duplicates
        all_teams = np.unique(all_teams)

        # mapper to extract team keys out
        def map_team_keys(dict):
            team_names = []
            team_names.append(dict['red']['team_keys'][0])
            team_names.append(dict['red']['team_keys'][1])
            team_names.append(dict['red']['team_keys'][2])
            team_names.append(dict['blue']['team_keys'][0])
            team_names.append(dict['blue']['team_keys'][1])
            team_names.append(dict['blue']['team_keys'][2])
            return team_names

        all_matches['team_keys'] = all_matches['alliances'].map(map_team_keys)

        def clean_data(df, team_name):
            new_data = df.copy()
            new_data = new_data.join(get_team(df, team_name))
            new_data = new_data.join(get_opponents(new_data))
            new_data = new_data.join(get_score_data(new_data, team_name))
            new_data.drop(['actual_time', 'alliances', 'post_result_time', 'predicted_time', 'score_breakdown', 'videos', 'time'], axis=1, inplace=True)
            new_data.sort_values(by='match_number', inplace=True)
            new_data.reset_index(inplace=True)
            new_data.drop('index', axis=1, inplace=True)

            return new_data

        for team in all_teams:
            all_teams_matches[team] = all_matches.loc[all_matches['team_keys'].apply(lambda x: team in x)]
            all_teams_matches[team] = clean_data(all_teams_matches[team].reset_index().drop('index', axis=1), team)
            all_teams_matches[team].to_csv(f'teams_data/{team}data.csv', index=False)
        

        print('all done!')

        
    def get_good_events():
        bad_events = pd.read_csv('bad_events.csv')
        all_events = list(pd.read_json(requests.get('https://www.thebluealliance.com/api/v3/events/2022/keys', header).text)[0])
        bad_events_actual = np.unique(list(bad_events['BadEvents']))
        print(bad_events_actual)
        for event in bad_events_actual:
            all_events.remove(event)
        return all_events

    load_data(get_good_events())