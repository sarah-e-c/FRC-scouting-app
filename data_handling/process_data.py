# this is a file that is a bit better! 
from multiprocessing import Event
import pandas as pd
import requests
import time
import numpy as np
import statistics
import os
import match_selector as selector
import math
import logging
import sqlite3
from sqlite3 import Error
from utils import Constants
from data_handling import Session, engine, Base
from data_handling import models
from sqlalchemy.sql import text
from sqlalchemy import Integer, String, Float
import statistics


#must send key with header 
HEADER = {'X-TBA-Auth-Key': Constants.KEY}
YEAR = 2022

logger = logging.getLogger(__name__)


# first method -- unneeded
def get_api_data(data_loaded=False, verbose=True, event_keys='default', match_data_filepath='all_matches_uncleaned.json'):
    """
    Method to grab all of the data needed for the program from the Blue Alliance api.
    data_loaded -- signify if data is loaded already. (mostly for testing, usually you wouldn't have to run this method at all)
    verbose -- signify if print statements/logs are wanted
    event_keys -- pass 'default' for default list of events, pass 'all' for all good events for year, or pass in custom list of event keys
    match_data_filepath -- filepath where the wanted matches will be saved in a json
    """
    if verbose:
        logger.debug('getting data from api...')
    def get_score_data(df, team_name):

        taxied_list = []
        endgames_list = []

        auto_lower_points_list = []
        auto_upper_points_list = []
        tele_lower_points_list = []
        tele_upper_points_list = []

        total_team_points_list = []
        won_game_list = []
        week_list = []


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
            except Exception as e:
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
            
        # week
        week_list = [-1] * len(taxied_list)
        for i in range(5):
            current_week_indexes = selector.select_by_event_week([i], df)
            for index in current_week_indexes:
                week_list[index] = i
        


        return pd.DataFrame({'Taxied': taxied_list,
                            'Hang': endgames_list,
                            'TeamAutoLower': auto_lower_points_list,
                            'TeamAutoUpper': auto_upper_points_list,
                            'TeamTeleopLower': tele_lower_points_list,
                            'TeamTeleopUpper': tele_upper_points_list,
                            'TotalTeamPoints': total_team_points_list,
                            'WonGame': won_game_list,
                            'Week': week_list
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

    def load_data(good_event_list, data_preloaded=True):
        all_teams_matches = {}
        all_matches = []
        all_teams = [] # getting all teams

        # if the data is not already loaded into file, get data
        if not data_preloaded:
            for event in good_event_list:
                event_matches = pd.read_json(requests.get(f'https://www.thebluealliance.com/api/v3//event/{event}/matches', HEADER).text)
                all_matches.append(event_matches)
                time.sleep(0.2) # being nice
            
            # writing this to a csv so less requests
            all_matches = pd.concat(all_matches).reset_index()

            all_matches.to_json(match_data_filepath)

        all_matches = pd.read_json(match_data_filepath)
        all_matches = all_matches.loc[all_matches['event_key'].apply(lambda x: x in good_event_list)]


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
        


        
    def get_good_events(bad_events_filepath='bad_events.csv'):
        """
        method to separate the valid events from the invalid events. Assumes that bad events
        (unique not a requirement) are preloaded into a csv file.
        bad_events_filepath -- filepath where the bad events are loaded.
        **Future updates will have False as an option and will generate the bad events.
        """
        bad_events = pd.read_csv(bad_events_filepath)
        all_events = list(pd.read_json(requests.get(f'https://www.thebluealliance.com/api/v3/events/{YEAR}/keys', HEADER).text)[0])
        bad_events_actual = np.unique(list(bad_events['BadEvents']))
        for event in bad_events_actual:
            all_events.remove(event)
        return all_events


    if event_keys =='all':
        load_data(get_good_events(), data_preloaded=data_loaded)
    elif event_keys == 'default':
        default_events = [
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
        load_data(default_events, data_preloaded=data_loaded)
    else:
        try:
            load_data(event_keys, data_preloaded=data_loaded)
        except:
            pass


#second method for normal flow
def team_stats_process(directory='teams_data', 
                        verbose=True,
                        team_stats_filepath='all_team_stats.csv', 
                        late_weighting=False, 
                        included_weeks ='all',
                        sql_mode = False):
    """
    method that takes all of the teams data and compresses it into one file.
    directory='teams_data' -- folder that the team stats are in
    verbose=True -- True to print to console False to not
    team_stats_filepath='all_team_stats.csv' -- filepath for csv with team statistics. Pass False to return a pandas DataFrame
    late_weighting=False -- experimental feature where later matches are weighted more. 
        Enter False or number above 1. WARNING -- decimal values take longer to compute
    included_weeks='all' -- provide a list of weeks for the statistics to be computed. Enter -1 events that aren't in the week system.
    """

    if verbose:
        logger.debug('Condensing team averages...')
    
    if not sql_mode:
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

    def get_winrate_highest_level(df, late_weighting):
        if not sql_mode:
            try:
                if included_weeks != 'all':
                    df = df.loc[df['Week'].apply(lambda x: x in included_weeks)]
                if not late_weighting:
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
                else:
                    mapping_win = {'Yes': 1, 'Tie': 0.5, 'No': 0}
                    mapping_climb = {'None': 0, 'Low': 4, 'Mid': 8, 'High': 12, 'Traversal': 15}
                    mapping_match_level = {'f': 5, 'sf': 3, 'qm': 0}

                    # getting orders of the weeks that they are in
                    all_weeks = np.unique(df['Week'])
                    all_weeks = list(np.sort(all_weeks))

                    # empty is actually the last one
                    if all_weeks[0] is None:
                        all_weeks.remove(0)
                        all_weeks.append(-1)
                    mapping = {}
                    # assigning a weight value for each week
                    for index, week in enumerate(all_weeks):
                        mapping[week] = late_weighting ** index
                    df['week_weighting'] = df['Week'].map(mapping)

                    winrate_list.append(np.average(df['WonGame'].map(mapping_win), weights=df['week_weighting']))
                    hang_score_list.append(df['Hang'].map(mapping_climb).mean())


                    team_auto_lower_list.append(np.average(df['TeamAutoLower'], weights=df['week_weighting']))
                    team_auto_upper_list.append(np.average(df['TeamAutoUpper'], weights=df['week_weighting']))
                    team_tele_lower_list.append(np.average(df['TeamTeleopLower'], weights=df['week_weighting']))
                    team_tele_upper_list.append(np.average(df['TeamTeleopUpper'], weights=df['week_weighting']))
                    highest_comp_level_list.append(df['comp_level'].map(mapping_match_level).max())
            except Exception as e:
                
                winrate_list.append(0)
                hang_score_list.append(0)
                team_auto_lower_list.append(0)
                team_auto_upper_list.append(0)
                team_tele_lower_list.append(0)
                team_tele_upper_list.append(0)
                highest_comp_level_list.append(0)
                logger.warning(e)
        else: # sql mode on
            try:
                if included_weeks != 'all':
                    df = df.loc[df['week'].apply(lambda x: x in included_weeks)] # this looks bad
                if not late_weighting:
                    mapping = {1: 1, np.nan: 0.5, 0: 0}
                    winrate_list.append(df['won_game'].map(mapping).mean())
                    mapping_2 = {'None': 0, 'Low': 4, 'Mid': 8, 'High': 12, 'Traversal': 15}
                    hang_score_list.append(df['hang'].map(mapping_2).mean()) # hang score loaded in correctly?
                    team_auto_lower_list.append(df['alliance_auto_cargo_lower'].mean())
                    team_auto_upper_list.append(df['alliance_auto_cargo_upper'].mean())
                    team_tele_lower_list.append(df['alliance_teleop__cargo_lower'].mean())
                    team_tele_upper_list.append(df['alliance_teleop__cargo_upper'].mean())
                    mapping_3 = {'f': 7, 'sf': 5, 'qm': 0, 'qf': 3}
                    highest_comp_level_list.append(df['comp_level'].map(mapping_3).max())
                else:
                    mapping_win = {'Yes': 1, 'Tie': 0.5, 'No': 0}
                    mapping_climb = {'None': 0, 'Low': 4, 'Mid': 8, 'High': 12, 'Traversal': 15}
                    mapping_match_level = {'f': 6, 'sf': 5, 'qm': 0, 'qf': 3}

                    # getting orders of the weeks that they are in
                    all_weeks = np.unique(df['week'])
                    all_weeks = list(np.sort(all_weeks))

                    # empty is actually the last one
                    if all_weeks[0] is None:
                        all_weeks.remove(0)
                        all_weeks.append(-1)
                    mapping = {}
                    # assigning a weight value for each week
                    for index, week in enumerate(all_weeks):
                        mapping[week] = late_weighting ** index
                    df['week_weighting'] = df['week'].map(mapping)

                    winrate_list.append(np.average(df['won_game'].map(mapping_win), weights=df['week_weighting']))
                    hang_score_list.append(df['hang'].map(mapping_climb).mean())


                    team_auto_lower_list.append(np.average(df['alliance_auto_cargo_lower'], weights=df['week_weighting']))
                    team_auto_upper_list.append(np.average(df['alliance_auto_cargo_upper'], weights=df['week_weighting']))
                    team_tele_lower_list.append(np.average(df['alliance_teleop__cargo_lower'], weights=df['week_weighting']))
                    team_tele_upper_list.append(np.average(df['alliance_teleop__cargo_upper'], weights=df['week_weighting']))
                    highest_comp_level_list.append(df['comp_level'].map(mapping_match_level).max())
            except Exception as e:
                
                winrate_list.append(0)
                hang_score_list.append(0)
                team_auto_lower_list.append(0)
                team_auto_upper_list.append(0)
                team_tele_lower_list.append(0)
                team_tele_upper_list.append(0)
                highest_comp_level_list.append(0)
                logger.warning(e)
    
    if not sql_mode:
        for path in team_paths:
            df = pd.read_csv(path)
            team_name_list.append(path.split('/')[1].split('data')[0]) # kind of sus but w/e
            get_winrate_highest_level(df, late_weighting)
    else:
        df = pd.read_sql(directory, engine)
        with engine.connect() as con:
            statement = text(f"""
            SELECT DISTINCT team_name FROM {directory}
            """)
            team_name_list = list(map(lambda x: x[0], con.execute(statement).all()))
        for team in team_name_list:
            select_team = text(f"""
            SELECT * FROM {directory}
            WHERE team_name = '{team}';
            """) # TODO
            df = pd.read_sql(select_team, engine, index_col='index')
            get_winrate_highest_level(df, late_weighting) #can definitely be rewritten as a query

    # loading final DataFrame
    try:
        total_scores_df = pd.DataFrame({ 'TeamName': team_name_list,
                            'WinRate': winrate_list,
                            'TeamAutoLower': team_auto_lower_list,
                            'TeamAutoUpper': team_auto_upper_list,
                            'TeamTeleopLower': team_tele_lower_list,
                            'TeamTeleopUpper': team_tele_upper_list,
                            'HangScore': hang_score_list,
                            'HighestCompLevel': highest_comp_level_list
                            })
    except Exception as e:
        logger.warning(e)
        logger.info(len(team_name_list))
        logger.info(winrate_list)
        raise e
    
    if not team_stats_filepath:
        total_scores_df.rename({'TeamName': 'team_name',
                                'WinRate': 'win_rate',
                                'TeamAutoLower': 'team_auto_lower',
                                'TeamAutoUpper': 'team_auto_upper',
                                'TeamTeleopLower': 'team_teleop_lower',
                                'TeamTeleopUpper': 'team_teleop_upper',
                                'HangScore': 'hang_score',
                                'HighestCompLevel': 'highest_comp_level'}, inplace=True, axis='columns')
        return total_scores_df
    if team_stats_filepath.endswith('.csv'):
        total_scores_df.to_csv(team_stats_filepath, index=False)
        logger.info('Fresh team statistics written to csv')
    else:
        total_scores_df.rename({'TeamName': 'team_name',
                                'WinRate': 'win_rate',
                                'TeamAutoLower': 'team_auto_lower',
                                'TeamAutoUpper': 'team_auto_upper',
                                'TeamTeleopLower': 'team_teleop_lower',
                                'TeamTeleopUpper': 'team_teleop_upper',
                                'HangScore': 'hang_score',
                                'HighestCompLevel': 'highest_comp_level'}, inplace=True, axis='columns')
        total_scores_df.to_sql(team_stats_filepath, engine,
                                index=False,
                                 if_exists='replace',
                                 dtype={
                                    'team_name': String,
                                    'win_rate': Float,
                                    'team_auto_lower': Float,
                                    'team_auto_upper': Float,
                                    'team_teleop_lower': Float,
                                    'team_teleop_upper': Float,
                                    'hang_score': Float,
                                    'highest_comp_level': Integer
                                 })
                                 
        logger.info('Fresh team statistics written to sql')
        return total_scores_df

#third method for normal flow
def load_matches_alliance_stats(event_keys='default', 
                                verbose=True, 
                                team_stats_filepath='all_team_stats.csv', 
                                all_matches_filepath='all_matches_uncleaned.json', 
                                all_matches_stats_filepath='all_matches_stats.csv',
                                enable_sql =True):
    """
    method that matches all of the teams data to the selected event matches and puts them in a file.
    event_keys='default' -- 'default', 'all', or selected list of event keys. Default gives Chesapeake district events,
    'all' gives all found events, and a list of event keys will process those event keys.
    verbose=True -- True to print to the console, False to not
    team_stats_filepath='all_team_stats.csv' -- filepath where team statistics are loaded (from team_stats_process) -- or pass pandas df
    all_matches_filepath -- filepath where all of the wanted matches are loaded in -- or pass pandas df
    all_matches_stats_filepath -- filepath where all of the matches' statistics are loaded in. -- or return pandas df
    connection='False' -- if using sql, pass the sqlalchemy session
    """

    if verbose:
        logger.debug('Loading alliance statistics...')

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
        if not enable_sql:
            for team in team_list:
                team_winrate_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['WinRate']))
                team_auto_lower_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['TeamAutoLower']))
                team_auto_upper_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['TeamAutoUpper']))
                team_teleop_lower_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['TeamTeleopLower']))
                team_teleop_upper_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['TeamTeleopUpper']))
                team_hang_score_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['HangScore']))
                team_highest_comp_level_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['HighestCompLevel']))
        else: # sql enabled
            for team in team_list:
                try:
                    team_winrate_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['win_rate']))
                    team_auto_lower_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['team_auto_lower']))
                    team_auto_upper_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['team_auto_upper']))
                    team_teleop_lower_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['team_teleop_lower']))
                    team_teleop_upper_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['team_teleop_upper']))
                    team_hang_score_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['hang_score']))
                    team_highest_comp_level_list.append(float(team_stats_df.loc[team_stats_df['team_name'] == team]['highest_comp_level']))
                except Exception as e:
                    logger.warning(e)
                    team_winrate_list.append(0)
                    team_auto_lower_list.append(0)
                    team_auto_upper_list.append(0)
                    team_teleop_lower_list.append(0) # need to make this for each one --
                    team_teleop_upper_list.append(0)
                    team_hang_score_list.append(0)
                    team_highest_comp_level_list.append(0)
        
        # returning the wanted meta statistics in a series (for a dataframe)
        return_series =  pd.Series({
                            #'' TODO
                            
                            'AvgWinrate': statistics.mean(team_winrate_list),
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
        logger.debug(return_series)
        return return_series

    def get_teams(match_df):
        """
        method that takes in an uncleaned read json file for a single match
        and returns a DataFrame with the team keys sorted into red and blue. (for clean_data method)
        match_dictionary_table_name='match_dictionary' -- table name of the match dictionary
        match_df -- pandas DataFrame with wanted uncleaned match data from the api.
        """
        red_teams_list = []
        blue_teams_list = []
        if not enable_sql:
            for i in range(match_df.shape[0]):
                red_teams_list.append(match_df.iloc[i]['alliances']['red']['team_keys'])
                blue_teams_list.append(match_df.iloc[i]['alliances']['blue']['team_keys'])
        else:
            for i in range(match_df.shape[0]):
                red_teams_list.append([match_df.iloc[i]['red_team_1'], match_df.iloc[i]['red_team_2'], match_df.iloc[i]['red_team_3']])
                blue_teams_list.append(match_df.iloc[i][['blue_team_1', 'blue_team_2', 'blue_team_3']])
        return pd.DataFrame({'Red': red_teams_list, 'Blue': blue_teams_list})


    def get_team_stats(match_df, team_stats_df):
        
        """
        method that gets team averages 
        match_df -- pandas DataFrame with wanted uncleaned match data from the api.
        team_stats_df -- dataframe with all of the team averages loaded in (from team_stats_process)
        """
        def get_team_averages(team_list_df, team_stats_df):
            """
            Method that takes a list of teams and team info and returns a series with all of the team stats.
            team_list_df -- dataframe with teams sorted into red and blue.
            team_stats_df -- dataframe with all of the team averages loaded in
            """
            series_list = []
            for i in range(team_list_df.shape[0]):
                team_info_red = team_lookup_averages(team_list_df.iloc[i]['Red'], team_stats_df).rename('Red Averages')
                team_info_blue = team_lookup_averages(team_list_df.iloc[i]['Blue'], team_stats_df).rename('Blue Averages')
                series_list.append(team_info_red - team_info_blue)

            return pd.DataFrame(series_list)
        
        teams_names_df = get_teams(match_df)
        winner_series = match_df['winning_alliance'].map({'red': 1, '': 0, 'blue': -1, None:0})
        key_series = match_df['key']
        event_key_series = match_df['event_key']

        return get_team_averages(teams_names_df, team_stats_df).join(match_df['event_key']).join(winner_series).join(key_series).join(event_key_series)
    
    # checking if it is a csv file
    try:
        if team_stats_filepath.endswith('.csv'):
            team_stats_dataframe = pd.read_csv(team_stats_filepath)
        # if not csv, then is sql table
        elif type(team_stats_filepath) == str:
            team_stats_dataframe = pd.read_sql(team_stats_filepath, engine)
    except:
        # if its not a string, its a dataframe
        team_stats_dataframe = team_stats_filepath
    # if not this, then is dataframe


    if type(event_keys) == str:
        if event_keys == 'default':
            #chesapeake area event keys -- default
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
        elif event_keys == 'all':
            if all_matches_filepath.endswith('.json'):
                temp_df = pd.read_json(all_matches_filepath)
            elif type(all_matches_filepath) == str:
                temp_df = pd.read_sql(all_matches_filepath, engine)
            else:
                temp_df = all_matches_filepath

            matches_data = temp_df
    else:

        if all_matches_filepath.endswith('json'):
            temp_df = pd.read_json(all_matches_filepath)
        elif type(all_matches_filepath) == str:
            temp_df = pd.read_sql(all_matches_filepath, engine)
        else:
            temp_df = all_matches_filepath
            matches_data = temp_df
        # for event in event_keys:
        #     # source = requests.get(f'https://www.thebluealliance.com/api/v3/event/{event}/matches', HEADER).text #should be rewritten
        #     # matches_data_list.append(pd.read_json(source))
        #     # time.sleep(0.3)
        #     # print(event, ' is loaded!')
        
        temp_df = temp_df.loc[temp_df['event_key'].apply(lambda x: x in event_keys)]
    
    matches_data = temp_df
    all_matches_data = []
    all_matches_data.append(get_team_stats(matches_data, team_stats_dataframe))

    # all_matches_data is a list of dataframes
    try:
        all_matches_df = pd.concat(all_matches_data)
    except Exception as e:
        logger.critical(e)
        all_matches_df = None
        raise e
    try: 
        if all_matches_stats_filepath.endswith('.csv'):
            all_matches_df.to_csv(all_matches_stats_filepath)
        elif type(all_matches_stats_filepath) == str:
            all_matches_df.rename({'AvgWinrate': 'avg_winrate',
                                    'HighestAvgWinrate': 'highest_avg_winrate',
                                    'LowestAvgWinrate': 'lowest_avg_winrate',
                                    'AvgAutoLower': 'avg_auto_lower',
                                    'HighestAutoLower': 'highest_auto_lower',                       
                                    'AvgAutoUpper': 'avg_auto_upper',
                                    'HighestAutoUpper': 'highest_auto_upper',             
                                    'AvgTeleopLower': 'avg_teleop_lower',
                                    'HighestTelopLower': 'highests_teleop_lower',
                                    'AvgTelopUpper': 'avg_teleop_upper',
                                    'HighestTelopUpper': 'highest_teleop_upper',
                                    'LowestTelopUpper': 'lowest_teleop_upper',
                                    'AvgHangScore': 'avg_hang_score',      
                                    'AvgHighestCompLevel': 'avg_highest_comp_level'}, 
                                    inplace=True, 
                                    axis='columns')
            all_matches_df.to_sql(all_matches_stats_filepath, engine,
                                index=False, if_exists='replace',
                                dtype={
                                        'key': String,
                                        'avg_winrate': Float,
                                        'highest_avg_winrate': Float,
                                        'lowest_avg_winrate': Float,
                                        'avg_auto_lower': Float,
                                        'highest_auto_lower': Float,
                                        'avg_auto_upper': Float,
                                        'highest_auto_upper': Float,
                                        'avg_teleop_lower': Float,
                                        'highest_teleop_lower': Float,
                                        'avg_teleop_upper': Float,
                                        'highest_teleop_upper': Float,
                                        'lowest_teleop_upper': Float,
                                        'avg_hang_score': Float,
                                        'avg_highest_comp_level': Float,
                                        'event_key': String,
                                        'winning_alliance': Integer
                                })
            logger.debug('written to sql.')
    except Exception as e:
        logger.debug('caught exception -- returning dataframe')
        logger.debug(all_matches_df.sample(5))
        all_matches_df.rename({'AvgWinrate': 'avg_winrate',
                                'HighestAvgWinrate': 'highest_avg_winrate',
                                'LowestAvgWinrate': 'lowest_avg_winrate',
                                'AvgAutoLower': 'avg_auto_lower',
                                'HighestAutoLower': 'highest_auto_lower',                       
                                'AvgAutoUpper': 'avg_auto_upper',
                                'HighestAutoUpper': 'highest_auto_upper',             
                                'AvgTeleopLower': 'avg_teleop_lower',
                                'HighestTelopLower': 'highests_teleop_lower',
                                'AvgTelopUpper': 'avg_teleop_upper',
                                'HighestTelopUpper': 'highest_teleop_upper',
                                'LowestTelopUpper': 'lowest_teleop_upper',
                                'AvgHangScore': 'avg_hang_score',      
                                'AvgHighestCompLevel': 'avg_highest_comp_level'}, 
                                inplace=True, 
                                axis='columns')
        return all_matches_df

# replacement for event selector


class FilterObject():
    """
    Class to streamline filtering match data. This will pass all of the information necessary to filter out data.
    """
    def __init__(self, event_filter=False, week_filter=False, district_filter=False, team_filter=False):
        self.event_filter = event_filter
        self.week_filter = week_filter
        self.district_filter = district_filter
        self.team_filter = team_filter

    def give_matches_sqlalchemy_objects(self, TableModel:Base, EventsTable: Base):
        """
        Method that is used to give the models of the matches sqlalchemy objects
        TableModel: sqlalchemy model of table getting from
        """
        # TODO make this better 
        session = Session()
        return session.query(TableModel).filter(TableModel.event_key.in_(self.get_events()), TableModel.event_key.in_(self.get_events_by_week(EventsTable))).all() # TODO use _in instead of in
            
    
    def give_matches_sqlalchemy_objects_one_column(self, TableModel:Base, column_name:str) -> list:
        """
        Method that is used to give the values of a single column.
        TableModel: sqlalchemy model of the given table
        column_name: name of column wanted
        """
        return_list = []
        session = Session()
        all_objects = session.query(TableModel).filter(TableModel.event_key.in_(self.get_events()), TableModel.week_filter in self.get_weeks())
        for object in all_objects:
            return_list.append(object.__getattr__(column_name))
        return return_list


    def add_event_filter(self, included_events=[]):
        """
        Method to replace the included events of the event filter
        """
        self.event_filter.replace_event_filter(included_events)

    def add_week_filter(self, included_weeks=[]):
        """
        Method to replace the filter for included weeks
        """
        self.week_fliter.replace_week_filter(included_weeks)

    def get_weeks(self,to_string=False):
        """
        wrapper method around the event filter getweeks
        """
        if not not self.week_filter: # if the week filter isn't False
            return self.week_filter.get_weeks(to_string=to_string)
        else:
            if to_string:
                return '-1, 0, 1, 2, 3, 4, 5'
            return [-1,0,1,2,3,4,5]

    def get_events_by_week(self, EventsTable: Base, to_string=False):
        """
        getting keys for events by the filter they were from.
        EventsTable: Base -- the table where all of the events data is held
        """
        if not not self.week_filter:
            return self.week_filter.get_events_by_week()
        else:
            session = Session()
            return_list = []
            events = session.query(EventsTable.event_key).all()
            return events


    def get_events(self, to_string=False):
        if not not self.event_filter:
            return self.event_filter.get_events(to_string=to_string)
        else:
            if to_string:
                0 # TODO
            return 0

class EventFilterObject():
    """
    Event filter object
    """
    def __init__(self, DictionaryModel:Base, included_events=[-1,0,1,2 ,3,4,5], complex=False):
        self.complex = complex
        if included_events == 'all':
            session = Session()
            events = []
            q_result = session.query(DictionaryModel).all()
            for item in q_result:
                events.append(item.event_key)
            self.included_events= list(np.unique(events))
        else:
            self.included_events = included_events
    
    def get_events(self, to_string=False):
        if not self.complex:
            if not to_string:
                return self.included_events
            else: # to_string is true
                return str(self.included_events).split('[')[1].split(']')[0]

    
    def replace_event_filter(self, included_events):
        """
        method to replace the event filter with a new one with different included events
        included_events: list of event keys
        """
        self.included_events = included_events
        logger.debug('replaced event filter')

class WeekFilterObject():
    """
    Event filter object
    """
    def __init__(self, EventTableModel, included_weeks=[-1,0,1,2,3,4,5], complex=False):
        self.complex = complex
        if included_weeks == 'all':
            included_weeks = [-1,0,1,2,3,4,5]
        self.included_weeks = included_weeks
        self.EventsTableModel = EventTableModel
    def get_weeks(self, to_string=False):
        if not self.complex:
            if not to_string:
                return self.included_weeks
            else: # to_string is true
                return str(self.included_weeks).split('[')[1].split(']')[0]
        
    def get_events_by_week(self, to_string=False):
        if self.included_weeks == 'all':
            session = Session()
            events = []
            q_result = session.query(self.EventsTableModel).all()
            for item in q_result:
                events.append(item.key)
            return list(np.unique(events))
        else:
            session = Session()
            events = []
            q_result = session.query(self.EventsTableModel.key).filter(self.EventsTableModel.week.in_(self.included_weeks)).all()
            for item in q_result:
                events.append(item.key)
            if not to_string:
                return list(np.unique(events))
            else: # to_string is true
                return str(events).split('[')[1].split(']')[0]


    
    def replace_week_filter(self, included_weeks):
        self.included_weeks = included_weeks
        logger.debug('replaced week filter')



def get_basic_filter(included_weeks=False, included_events=False) -> FilterObject:
    """
    A method to create a basic filter object
    """
    if not not included_events: # idk if this works or not
        event_filter = EventFilterObject(included_events=included_events, DictionaryModel=models.MatchDictionary)

    if not not included_weeks:
        week_filter = WeekFilterObject(included_weeks=included_weeks, EventTableModel=models.Event)
    return FilterObject(event_filter=event_filter, week_filter=week_filter)
    


def team_stats_process_full_sql(matches_table_name='match_expanded_tba',
                                output_table_name='teams_profile_all_weeks',
                                filter=get_basic_filter(included_events='all', included_weeks='all'),
                                late_weighting = False):
    """
    A method to process team stats using full sql.
    matches_table_name = table name with all of the match data -- usually match_expanded_tba
    output_table_name = table name where the new data will be pushed to
    late_weighting = False: determine whether to weight the later weeks more. results in different
    """

    valid_weeks_string = filter.get_weeks(to_string=True)
    valid_events_string = filter.get_events(to_string=True)

    create_output_query = f"""
    CREATE TABLE IF NOT EXISTS {output_table_name} (
        team_name TEXT,
        win_rate FLOAT,
        highest_comp_level INTEGER,
        team_auto_lower FLOAT,
        team_auto_upper FLOAT,
        team_teleop_lower FLOAT,
        team_teleop_upper FLOAT,
        hang_score FLOAT
    )

    """
    dlt_query = f"""
    DELETE FROM {output_table_name};
    """
    con = engine.connect()
    con.execute(create_output_query)
    con.execute(dlt_query)
    logger.debug('previous data dropped from table')



    if not late_weighting: # makes no distinction between weeks
        query = f"""INSERT INTO {output_table_name} (team_name, win_rate, highest_comp_level, team_auto_lower, team_auto_upper, team_teleop_lower, team_teleop_upper, hang_score)
        SELECT team_name,
        AVG(won_game) AS win_rate,
        MAX(CASE comp_level WHEN 'qm' THEN 0 WHEN 'qf' THEN 3 WHEN 'sf' THEN 5 WHEN 'f' THEN 7 ELSE 0 END) AS highest_comp_level,
        AVG(alliance_auto_cargo_lower) AS team_auto_lower,
        AVG(alliance_auto_cargo_upper) AS team_auto_upper,
        AVG(alliance_teleop__cargo_lower) AS team_teleop_lower,
        AVG(alliance_teleop__cargo_upper) AS team_teleop_upper,
        AVG(hang) AS hang_score
        FROM {matches_table_name}
        WHERE week IN ({valid_weeks_string}) AND event_key in ({valid_events_string})
        GROUP BY team_name;
        """
        con.execute(query)
    else:
        TEMP_TABLE_NAME = 'temp_data_processing'
        query_create = f"""
        CREATE TABLE IF NOT EXISTS {TEMP_TABLE_NAME} (
            team_name TEXT,
            win_rate FLOAT,
            highest_comp_level INTEGER,
            team_auto_lower FLOAT,
            team_auto_upper FLOAT,
            team_teleop_lower FLOAT,
            team_teleop_upper FLOAT,
            hang_score FLOAT,
            weight FLOAT
        );
        """
        con.execute(query_create)
        

        # creating weights
        weights = []
        for index, week in enumerate(filter.get_weeks()):
            weights.append((index + 1) ** late_weighting)
        
        # for each week, calculate the averages, then combine all of them
        for weight, week in zip(weights, filter.get_weeks()):
            step_query = f"""INSERT INTO {TEMP_TABLE_NAME} (team_name, win_rate, highest_comp_level, team_auto_lower, team_auto_upper, team_teleop_lower, team_teleop_upper, hang_score, weight)
            SELECT team_name,
            AVG(won_game) AS win_rate,
            MAX(CASE comp_level WHEN 'qm' THEN 0 WHEN 'qf' THEN 3 WHEN 'sf' THEN 5 WHEN 'f' THEN 7 ELSE 0 END) AS highest_comp_level,
            AVG(alliance_auto_cargo_lower) AS team_auto_lower,
            AVG(alliance_auto_cargo_upper) AS team_auto_upper,
            AVG(alliance_teleop__cargo_lower) AS team_teleop_lower,
            AVG(alliance_teleop__cargo_upper) AS team_teleop_upper,
            AVG(hang) AS hang_score,
            {weight} AS weight
            FROM {matches_table_name}
            WHERE week = {week} AND event_key in ({valid_events_string})
            GROUP BY team_name;
            """
            con.execute(step_query)
            logger.debug(f'week {week} data processed -- getting to be late weighted.')
        

        compression_query = f"""
            INSERT INTO {output_table_name} (team_name, win_rate, highest_comp_level, team_auto_lower, team_auto_upper, team_teleop_lower, team_teleop_upper, hang_score)
            SELECT team_name,
            SUM(win_rate * weight) / SUM(weight) AS win_rate,
            MAX(highest_comp_level * weight)/ SUM(weight) AS highest_comp_level,
            SUM(team_auto_lower * weight)/ SUM(weight) AS team_auto_lower,
            SUM(team_auto_upper * weight)/ SUM(weight) AS team_auto_upper,
            SUM(team_teleop_lower * weight)/ SUM(weight) AS team_teleop_lower,
            SUM(team_teleop_upper * weight)/ SUM(weight) AS team_teleop_upper,
            SUM(hang_score * weight)/ SUM(weight) AS hang_score
            FROM {TEMP_TABLE_NAME}
            GROUP BY team_name;
        
        """
        con.execute(compression_query)
        logger.debug('weighted query submitted')

        dlt_temp_query = f"""
        DROP TABLE {TEMP_TABLE_NAME}
        """
        con.execute(dlt_temp_query)
    
    
    logger.debug('teams data processed')
    

def load_matches_alliance_stats_full_sql(matches_dictionary_table_name='match_dictionary',
                                         team_stats_table_name='teams_profile_all_weeks',
                                         output_table_name='all_matches_stats_all_weeks',
                                         events_table_name='events',
                                         filter=get_basic_filter(included_events='all', included_weeks='all'),
                                         delete_existing=True):
    """
    matches_dictionary_table_name = 'match_dictionary' name of table of dictionary of matches 
    team_stats_table_name = 'teams_profile_all_weeks' name of table of teams profile
    output_table_name = 'all_matches_stats_all_weeks' name of table of output
    filter - FilterObject used to get the wanted data
    delete_existing=True: if set to false, then the existing data in the table will not be deleted before inserting rest
    """

    # getting model classes from names
    MatchesDictionaryModel  = models.table_name_to_model[matches_dictionary_table_name]
    TeamStatsModel = models.table_name_to_model[team_stats_table_name]
    OutputTableModel = models.table_name_to_model[output_table_name]
    EventsTableModel = models.table_name_to_model[events_table_name]

    con = engine.connect() # connection 

    # creating the output table if it doesn't exist yet
    crt_stmt = f"""
    CREATE TABLE IF NOT EXISTS {output_table_name} (
        key TEXT,
        avg_winrate  FLOAT,
        highest_avg_winrate FLOAT,
        lowest_avg_winrate  FLOAT,
        avg_auto_lower FLOAT,
        highest_auto_lower  FLOAT,
        avg_auto_upper  FLOAT,
        highest_auto_upper  FLOAT,
        avg_teleop_lower FLOAT,
        highest_teleop_lower FLOAT,
        avg_teleop_upper FLOAT,
        highest_teleop_upper FLOAT,
        lowest_teleop_upper FLOAT,
        avg_hang_score  FLOAT,
        avg_highest_comp_level FLOAT,
        event_key TEXT,
        winning_alliance TEXT
    );
    """
    # deleting existing records if they exist
    dlt_stmt = f"""
    DELETE FROM {output_table_name};
    """


    con.execute(crt_stmt) # creating the table if its not there

    if delete_existing:
        con.execute(dlt_stmt) # deleting from the table
        logger.debug('existing data deleted from matches table')

    # default if team name cannot be found
    default_team_stat = TeamStatsModel(
        win_rate=0.25,
        team_auto_lower=0,
        team_auto_upper=1,
        team_teleop_lower=0,
        team_teleop_upper=5,
        hang_score=0,
        highest_comp_level=0
    )
    session = Session()
    problematic_team_names = []
    problematic_matches = []
    for match in filter.give_matches_sqlalchemy_objects(MatchesDictionaryModel, EventsTableModel):
        try:
            red_team_1_stat = session.query(TeamStatsModel).filter_by(team_name=match.red_team_1).one()
        except Exception as e:
            problematic_team_names.append(match.red_team_1)
            red_team_1_stat = default_team_stat
        
        try:
            red_team_2_stat = session.query(TeamStatsModel).filter_by(team_name=match.red_team_2).one()
        except Exception as e:
            problematic_team_names.append(match.red_team_2)
            red_team_2_stat = default_team_stat
        try: 
            red_team_3_stat = session.query(TeamStatsModel).filter_by(team_name=match.red_team_3).one()
        except Exception as e:
            problematic_team_names.append(match.red_team_3)
            red_team_3_stat = default_team_stat
        
        try:
            blue_team_1_stat = session.query(TeamStatsModel).filter_by(team_name=match.blue_team_1).one()
        except Exception as e:
            problematic_team_names.append(match.blue_team_1)
            blue_team_1_stat = default_team_stat
        
        try:
            blue_team_2_stat = session.query(TeamStatsModel).filter_by(team_name=match.blue_team_2).one()
        except Exception as e:
            problematic_team_names.append(match.blue_team_2)
            blue_team_2_stat = default_team_stat
        
        try:
            blue_team_3_stat = session.query(TeamStatsModel).filter_by(team_name=match.blue_team_3).one()
        except Exception as e:
            problematic_team_names.append(match.blue_team_3)
            blue_team_3_stat = default_team_stat
        try:
            match_stats = OutputTableModel(
                key = match.key,
                avg_winrate = statistics.mean([red_team_1_stat.win_rate, red_team_2_stat.win_rate, red_team_3_stat.win_rate]) - statistics.mean([blue_team_1_stat.win_rate, blue_team_2_stat.win_rate, blue_team_3_stat.win_rate]),
                highest_avg_winrate = max([red_team_1_stat.win_rate, red_team_2_stat.win_rate, red_team_3_stat.win_rate]) - max([blue_team_1_stat.win_rate, blue_team_2_stat.win_rate, blue_team_3_stat.win_rate]),
                lowest_avg_winrate = min([red_team_1_stat.win_rate, red_team_2_stat.win_rate, red_team_3_stat.win_rate]) - min([blue_team_1_stat.win_rate, blue_team_2_stat.win_rate, blue_team_3_stat.win_rate]),
                avg_auto_lower = statistics.mean([red_team_1_stat.team_auto_lower, red_team_2_stat.team_auto_lower, red_team_3_stat.team_auto_lower]) - statistics.mean([blue_team_1_stat.team_auto_lower, blue_team_2_stat.team_auto_lower, blue_team_3_stat.team_auto_lower]),
                highest_auto_lower = max([red_team_1_stat.team_auto_lower, red_team_2_stat.team_auto_lower, red_team_3_stat.team_auto_lower]) - max([blue_team_1_stat.team_auto_lower, blue_team_2_stat.team_auto_lower, blue_team_3_stat.team_auto_lower]),
                avg_auto_upper = statistics.mean([red_team_1_stat.team_auto_upper, red_team_2_stat.team_auto_upper, red_team_3_stat.team_auto_upper]) - statistics.mean([blue_team_1_stat.team_auto_upper, blue_team_2_stat.team_auto_upper, blue_team_3_stat.team_auto_upper]),
                highest_auto_upper = max([red_team_1_stat.team_auto_upper, red_team_2_stat.team_auto_upper, red_team_3_stat.team_auto_upper]) - max([blue_team_1_stat.team_auto_upper, blue_team_2_stat.team_auto_upper, blue_team_3_stat.team_auto_upper]),
                avg_teleop_lower = statistics.mean([red_team_1_stat.team_teleop_lower, red_team_2_stat.team_teleop_lower, red_team_3_stat.team_teleop_lower]) - statistics.mean([blue_team_1_stat.team_teleop_lower, blue_team_2_stat.team_teleop_lower, blue_team_3_stat.team_teleop_lower]),
                highest_teleop_lower = max([red_team_1_stat.team_teleop_lower, red_team_2_stat.team_teleop_lower, red_team_3_stat.team_teleop_lower]) - max([blue_team_1_stat.team_teleop_lower, blue_team_2_stat.team_teleop_lower, blue_team_3_stat.team_teleop_lower]),
                avg_teleop_upper = statistics.mean([red_team_1_stat.team_teleop_upper, red_team_2_stat.team_teleop_upper, red_team_3_stat.team_teleop_upper]) - statistics.mean([blue_team_1_stat.team_teleop_upper, blue_team_2_stat.team_teleop_upper, blue_team_3_stat.team_teleop_upper]),
                highest_teleop_upper = max([red_team_1_stat.team_teleop_upper, red_team_2_stat.team_teleop_upper, red_team_3_stat.team_teleop_upper]) - max([blue_team_1_stat.team_teleop_upper, blue_team_2_stat.team_teleop_upper, blue_team_3_stat.team_teleop_upper]),
                lowest_teleop_upper = min([red_team_1_stat.team_teleop_upper, red_team_2_stat.team_teleop_upper, red_team_3_stat.team_teleop_upper]) - min([blue_team_1_stat.team_teleop_upper, blue_team_2_stat.team_teleop_upper, blue_team_3_stat.team_teleop_upper]),
                avg_hang_score = statistics.mean([red_team_1_stat.hang_score, red_team_2_stat.hang_score, red_team_3_stat.hang_score]) - max([blue_team_1_stat.hang_score, blue_team_2_stat.hang_score, blue_team_3_stat.hang_score]),
                avg_highest_comp_level = statistics.mean([red_team_1_stat.highest_comp_level, red_team_2_stat.highest_comp_level, red_team_3_stat.highest_comp_level]) - statistics.mean([blue_team_1_stat.highest_comp_level, blue_team_2_stat.highest_comp_level, blue_team_3_stat.highest_comp_level]),
                event_key = match.event_key,
                winning_alliance = match.winning_alliance
            )
            session.add(match_stats)
        except Exception as e:
            problematic_matches.append(match.key)
    session.commit()
    logger.debug('written to sql')
    if len(problematic_team_names) > 0:
        logger.warning(f'problematic team names: {list(np.unique(problematic_team_names))}')
    if len(problematic_matches) > 0:
        logger.warning(f'problematic matches: {list(np.unique(problematic_matches))}')

def clear_temp_tables():
    session = Session()
    session.query(models.TempMatch).delete()
    session.query(models.TempTeamsProfileWeek0).delete()
    session.query(models.TempTeamsProfileWeek1).delete()
    session.query(models.TempTeamsProfileWeek2).delete()
    session.query(models.TempTeamsProfileWeek3).delete()
    session.query(models.TempTeamsProfileWeek4).delete()
    session.query(models.TempTeamsProfileWeek5).delete()
    session.query(models.TempTeamsProfileWeek10).delete()
    session.commit()
    session.close()

if __name__ == '__main__':
    import time
    start = time.time()
    team_stats_process_full_sql(late_weighting=1.5)
    load_matches_alliance_stats_full_sql()
    print('total time: ', time.time() - start, ' seconds')
    # get_api_data(data_loaded=True, event_keys='all')
    #team_stats_process(late_weighting=False, sql_mode=True, team_stats_filepath='teams_profile_all_weeks', directory='match_expanded_tba')
    #print(load_matches_alliance_stats(event_keys='all', all_matches_stats_filepath=False))
    #team_stats_process(directory='match_expanded_tba', team_stats_filepath='teams_profile_all_weeks', late_weighting=1.5, sql_mode=True)
    # logging.basicConfig(level=logging.DEBUG)
    # load_matches_alliance_stats('all', team_stats_filepath='teams_profile_all_weeks', all_matches_filepath='match_dictionary', all_matches_stats_filepath='all_matches_stats_all_weeks', enable_sql=True)
    # paths = []
    # for filename in os.scandir('teams_data'):
    #     if filename.is_file():
    #         paths.append(filename.path)
    # for path in paths:
    #     df = pd.read_csv(path)
    #     try: 
    #         _ = df['Week']
    #     except:
    #         os.remove(path)
    #         print('removed ', path)

            


