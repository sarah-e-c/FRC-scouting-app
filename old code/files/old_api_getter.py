import requests
import pandas as pd
import numpy as np
import time
import json
import os.path
import csv

#must send key with header (please dont steal my key  :()
header = {'X-TBA-Auth-Key': 'j5psodzpSE2HyqjKqVQUfC35jmvDo8Cb0YFHZN6ky76Arm4rQ7H2xD370QSwEmsC'}

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
            
            # auto lower
            total_auto_lower_points = (data_list['autoCargoLowerBlue'] +  data_list['autoCargoLowerFar']
                                        + data_list['autoCargoLowerNear'] + data_list['autoCargoLowerRed'])
            auto_lower_points_list.append(total_auto_lower_points)

            # auto upper
            total_auto_upper_points = (data_list['autoCargoUpperBlue'] +  data_list['autoCargoUpperFar']
                                        + data_list['autoCargoUpperNear'] + data_list['autoCargoUpperRed'])
            auto_upper_points_list.append(total_auto_upper_points)

            # teleop lower
            total_teleop_lower_points = (data_list['teleopCargoLowerBlue'] +  data_list['teleopCargoLowerFar']
                                        + data_list['teleopCargoLowerNear'] + data_list['teleopCargoLowerRed'])    
            tele_lower_points_list.append(total_teleop_lower_points)

            # teleop upper
            total_teleop_upper_points = (data_list['teleopCargoUpperBlue'] +  data_list['teleopCargoUpperFar']
                                        + data_list['teleopCargoUpperNear'] + data_list['teleopCargoUpperRed'])    
            tele_upper_points_list.append(total_teleop_upper_points)

            total_team_points_list.append(data_list['totalPoints'])
            if df.iloc[i]['team_alliance'] == df.iloc[i]['winning_alliance']:
                won_game_list.append('Yes')
            elif df.iloc[i]['winning_alliance'] == '': # checking if its nan
                won_game_list.append('Tie')
            else:
                won_game_list.append('No')
        except Exception as e:
            print(e)
            taxied_list.append(None)
            endgames_list.append(None)
            auto_lower_points_list.append(None)
            auto_upper_points_list.append(None)
            tele_lower_points_list.append(None)
            tele_upper_points_list.append(None)
            total_team_points_list.append(None)
            won_game_list.append(None)



    return pd.DataFrame({'Taxied': taxied_list,
                        'Hang': endgames_list,
                        'TeamAutoLower': auto_lower_points_list,
                        'TeamAutoUpper': auto_upper_points_list,
                        'TeamTeleopLower': tele_lower_points_list,
                        'TeamTeleopUpper': tele_upper_points_list,
                        'TotalTeamPoints': total_team_points_list,
                        'WonGame': won_game_list
     }) 


def clean_data(df, team_name, event, verbose=True):
    new_data = df.copy()
    new_data = new_data.join(get_team(df, team_name))
    new_data = new_data.join(get_opponents(new_data))
    new_data = new_data.join(get_score_data(new_data, team_name))
    try:
        new_data.drop(['actual_time', 'alliances', 'post_result_time', 'predicted_time', 'score_breakdown', 'videos', 'time'], axis=1, inplace=True)
        new_data.sort_values(by='match_number', inplace=True)
        new_data.reset_index(inplace=True)
        new_data.drop('index', axis=1, inplace=True)
    except Exception as e:
        print(event, 'is problematic')
        print(e)
        
    if verbose:
        print(f'{team_name}s data cleaned!')
    return new_data



# getting all va qualifier events... for now!
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

def fetch_events():
    event_keys = pd.read_json(requests.get('https://www.thebluealliance.com/api/v3/events/2022/keys', header).text)
    event_keys.to_csv('all_events.csv')
    event_keys = list(event_keys[0])
    return event_keys
    # test data 


# problematic events 

# dead
def remove_bad_events(event_keys):
    bad_events = ['2022cabl', '2022isi', '2022lloc', '2022mdbob', '2022mdbob2', '2022mikk', '2022mirc', '2022mirr', '2022mngggt', '2022mogw', '2022njbr2', '2022nmrc', '2022nmrc2', '2022nynew', '2022nyrr', '2022nyrra', '2022rsr', '2022srrc', '2022txntx', '2022txsg', '2022wimc', '2022zhha']

    for event in bad_events:
        event_keys.remove(event)
    
    event_keys.remove('2022chcmp')
    event_keys.remove('2022scsc')
    event_keys.remove('2022scsc2')
    event_keys.remove('2022iri')
    event_keys.remove('2022cmptx')
    event_keys.remove('2022ausc')
    event_keys.remove('2022cc')
    event_keys.remove('2022njbe')
    event_keys.remove('2022necmp')
    event_keys.remove('2022catt')
    event_keys.remove('2022txcmp')
    event_keys.remove('2022mikk2')
    event_keys.remove('2022micmp')
    event_keys.remove('2022nccmp')
    event_keys.remove('2022varr')
    event_keys.remove('2022vabrb')
    event_keys.remove('2022scsc3')
    return event_keys


def get_bad_events(event_list):
    bad_events = []
    for event in event_list:
        source = requests.get(f'https://www.thebluealliance.com/api/v3//event/{event}/matches', header).text
        try:
            df = pd.read_json(source)
            new_data = df.copy()
            team_name = str(df.iloc[0]['alliances']['red']['team_keys'][0])
            new_data = new_data.join(get_team(df, team_name))
            new_data = new_data.join(get_opponents(new_data))
            new_data = new_data.join(get_score_data(new_data, team_name))
            new_data.sort_values(by='match_number', inplace=True)
            new_data.reset_index(inplace=True)
            new_data.drop('index', axis=1, inplace=True)
        except Exception as e:
            print(event, e)
            bad_events.append(event)
        time.sleep(0.5) # being nice
    print(bad_events)
    return bad_events

def process_teams_events(verbose=True):
    all_teams_events = {}

    for event in event_keys:
        teams = requests.get(f'https://www.thebluealliance.com/api/v3/event/{event}/teams', header).text
        df = pd.read_json(teams)
        for i in range(df.shape[0]):
            if df.iloc[i]['key'] not in all_teams_events.keys():
                all_teams_events[df.iloc[i]['key']] = [event]
            else:
                all_teams_events[df.iloc[i]['key']].append(event)
        time.sleep(1) # being nice

    # print(all_teams_events)

    for team in all_teams_events.keys():
        team_dataframes = []
        for event in all_teams_events[team]:
            link = f'https://www.thebluealliance.com/api/v3/team/{team}/event/{event}/matches'
            source = requests.get(link, header).text
            data = pd.read_json(source)
            data_clean = clean_data(data, team, event)
            if verbose:
                print('cleaned ', event)
            team_dataframes.append(data_clean)
            time.sleep(1) # being nice
        all_data_clean = pd.concat(team_dataframes)
        all_data_clean.to_csv(f'teams_data/{team}data.csv')


