# this is a file that is a bit better! 
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
from gui.utils import Constants
from data_handling import engine
from sqlalchemy.sql import text


#must send key with header 
HEADER = {'X-TBA-Auth-Key': Constants.KEY}
YEAR = 2022

logging.basicConfig(level=logging.DEBUG)
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
                    df = df.loc[df['week'].apply(lambda x: x in included_weeks)]
                if not late_weighting:
                    mapping = {'Yes': 1, 'Tie': 0.5, 'No': 0}
                    winrate_list.append(df['won_game'].map(mapping).mean())
                    mapping_2 = {'None': 0, 'Low': 4, 'Mid': 8, 'High': 12, 'Traversal': 15}
                    hang_score_list.append(df['hang'].map(mapping_2).mean())
                    team_auto_lower_list.append(df['alliance_auto_cargo_lower'].mean())
                    team_auto_upper_list.append(df['alliance_auto_cargo_upper'].mean())
                    team_tele_lower_list.append(df['alliance_teleop__cargo_lower'].mean())
                    team_tele_upper_list.append(df['alliance_teleop__cargo_upper'].mean())
                    mapping_3 = {'f': 5, 'sf': 3, 'qm': 0}
                    highest_comp_level_list.append(df['comp_level'].map(mapping_3).max())
                else:
                    mapping_win = {'Yes': 1, 'Tie': 0.5, 'No': 0}
                    mapping_climb = {'None': 0, 'Low': 4, 'Mid': 8, 'High': 12, 'Traversal': 15}
                    mapping_match_level = {'f': 5, 'sf': 3, 'qm': 0}

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
        return total_scores_df
    if team_stats_filepath.endswith('.csv'):
        total_scores_df.to_csv(team_stats_filepath, index=False)
        logger.info('Fresh team statistics written to csv')
    else:
        total_scores_df.to_sql(team_stats_filepath, engine, if_exists='replace')
        logger.info('Fresh team statistics written to sql')

#third method for normal flow
def load_matches_alliance_stats(event_keys='default', 
                                verbose=True, 
                                team_stats_filepath='all_team_stats.csv', 
                                all_matches_filepath='all_matches_uncleaned.json', 
                                all_matches_stats_filepath='all_matches_stats.csv'):
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
        for team in team_list:
            team_winrate_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['WinRate']))
            team_auto_lower_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['TeamAutoLower']))
            team_auto_upper_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['TeamAutoUpper']))
            team_teleop_lower_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['TeamTeleopLower']))
            team_teleop_upper_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['TeamTeleopUpper']))
            team_hang_score_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['HangScore']))
            team_highest_comp_level_list.append(float(team_stats_df.loc[team_stats_df['TeamName'] == team]['HighestCompLevel']))
        
        # returning the wanted meta statistics in a series (for a dataframe)
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

    def get_teams(match_df):
        """
        method that takes in an uncleaned read json file for a single match
        and returns a DataFrame with the team keys sorted into red and blue. (for clean_data method)
        match_df -- pandas DataFrame with wanted uncleaned match data from the api.
        """
        red_teams_list = []
        blue_teams_list = []
        for i in range(match_df.shape[0]):
            red_teams_list.append(match_df.iloc[i]['alliances']['red']['team_keys'])
            blue_teams_list.append(match_df.iloc[i]['alliances']['blue']['team_keys'])
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
        winner_series = match_df['winning_alliance'].map({'red': 1, '': 0, 'blue': -1})

        return get_team_averages(teams_names_df, team_stats_df).join(match_df['event_key']).join(winner_series)
    
    # checking if it is a csv file
    if team_stats_filepath.endswith('.csv'):
        team_stats_dataframe = pd.read_csv(team_stats_filepath)
    # if not csv, then is sql table
    elif type(team_stats_filepath) == str:
        team_stats_dataframe = pd.read_sql(team_stats_filepath, engine)
    # if not this, then is dataframe
    else:
        team_stats_dataframe = team_stats_filepath

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
            elif type(all_matches_filepath) == 'str':
                temp_df = pd.read_sql(all_matches_filepath, engine)
            else:
                temp_df = all_matches_filepath
            matches_data = temp_df
    else:
        if all_matches_filepath == 'sql':
            temp_df = pd.read_sql(sql=all_matches_filepath, connection=engine)
        if type(all_matches_filepath) == str:
            temp_df = pd.read_json(all_matches_filepath)
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
    except:
        all_matches_df = None
    if all_matches_stats_filepath.endswith('.csv'):
        all_matches_df.to_csv(all_matches_stats_filepath)
    elif type(all_matches_stats_filepath) == str:
        all_matches_df.to_sql(all_matches_stats_filepath, engine)
    else:
        return all_matches_df

if __name__ == '__main__':
    
    # get_api_data(data_loaded=True, event_keys='all')
    #team_stats_process(late_weighting=1.5)
    #print(load_matches_alliance_stats(event_keys='all', all_matches_stats_filepath=False))
    team_stats_process(directory='match_expanded_tba', team_stats_filepath='teams_profile_all_weeks', late_weighting=1.5, sql_mode=True)

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

            


