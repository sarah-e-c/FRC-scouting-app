# run this file when running the app for the first time.
from concurrent.futures import process
import configparser
import secrets
from utils import Constants
import logging
import os
import json

import requests

logger = logging.getLogger(__name__)

def setup_application():




    # setting up config file
    settings_config = configparser.ConfigParser()

    settings_config.add_section('model')
    settings_config.set('model','late_weighting', '0.0')
    settings_config.set('model', 'mode', 'week_by_week')
    settings_config.set('model', 'type', 'XGBoost')

    # still need to configure included weeks
    settings_config.set('model','included_weeks', 'all')
    settings_config.add_section('user')
    settings_config.set('user', 'auth_key', secrets.token_hex(10)) # generating auth key
    settings_config.add_section('version')
    settings_config.set('version', 'version_number', Constants.VERSION)
    settings_config.set('version', 'version_type', Constants.VERSION_TYPE)
    settings_config.add_section('data')
    settings_config.set('data', 'tba_version', 'None')
    settings_config.set('data', 'dictionary_version', 'None')
    settings_config.set('data', 'user_extra_version', 'None')
    settings_config.set('data', 'events_version', 'None')
    with open('config.ini', 'w') as configfile:
        settings_config.write(configfile)

    if os.path.exists("data.db"):
        os.remove("data.db")

    # i know that this is cursed
    from data_handling import engine, session, Base
    from data_handling import models

    # grabbing match_expanded data from the api
    logger.info('creating database file')


    Base.metadata.create_all(engine)
    source = requests.get(f'{Constants.API_ENDPOINT}/get_match_data')
    logger.info(source.headers)
    settings_config.set('data', 'tba_version', source.headers['VersionTBAData'])
    data = json.loads(source.text)
    to_add = []
    for item in data:
        new_entry = models.MatchExpandedTBA(
            index = item['index'],
            team_name = item['team_name'],
            comp_level = item['comp_level'],
            event_key = item['event_key'],
            key = item['key'],
            match_number = item['match_number'],
            set_number = item['set_number'],
            winning_alliance = item['winning_alliance'],
            team_alliance = item['team_alliance'],
            teammate_1 = item['teammate_1'],
            teammate_2 = item['teammate_2'],
            teammate_3 = item['teammate_3'],
            opponent_1 = item['opponent_1'],
            opponent_2 = item['opponent_2'],
            opponent_3 = item['opponent_3'],
            taxied = item['taxied'],
            hang = item['hang'],
            alliance_auto_cargo_lower = item['alliance_auto_cargo_lower'],
            alliance_auto_cargo_upper = item['alliance_auto_cargo_upper'],
            alliance_teleop__cargo_lower = item['alliance_teleop__cargo_lower'],
            alliance_teleop__cargo_upper = item['alliance_teleop__cargo_upper'],
            won_game = item['won_game'],
            week = item['week']
        )

        to_add.append(new_entry)
    session.add_all(to_add)
    session.commit()
    logger.info('TBA match data written to sql')

    # grabbing match dictionary data from api
    logger.info('Grabbing match dictionary from api')
    source = requests.get(f'{Constants.API_ENDPOINT}/get_match_dictionary_data', {'User': settings_config.get('user', 'auth_key'), 'VersionDictionaryData': 'None'})
    settings_config.set('data', 'dictionary_version', source.headers['VersionDictionaryData'])
    data = json.loads(source.text)
    to_add = []
    for item in data:
        new_entry = models.MatchDictionary(
            key = item['key'],
            red_team_1 = item['red_team_1'],
            red_team_2 = item['red_team_2'],
            red_team_3 = item['red_team_3'],
            blue_team_1 = item['blue_team_1'],
            blue_team_2 = item['blue_team_2'],
            blue_team_3 = item['blue_team_3'],
            occurred = item['occurred'],
            winning_alliance= item['winning_alliance'],
            event_key = item['event_key'],
            comp_level = item['comp_level'],
            year = item['year'],
        )
        to_add.append(new_entry)
    session.add_all(to_add)
    session.commit()
    logger.info('match dictionary data written to sql')

    # grabbing user submitted match data from api
    logger.info('Grabbing additional user data from api')
    source = requests.get(f'{Constants.API_ENDPOINT}/get_user_expanded_match_data', {'User': settings_config.get('user', 'auth_key'), 'VersionDictionaryData': 'None'})
    settings_config.set('data', 'user_extra_version', source.headers['VersionUserSubmittedData'])
    data = json.loads(source.text)
    to_add = []
    for item in data:
        new_entry = models.MatchDictionary(
            key = item['key'],
            red_team_1 = item['red_team_1'],
            red_team_2 = item['red_team_2'],
            red_team_3 = item['red_team_3'],
            blue_team_1 = item['blue_team_1'],
            blue_team_2 = item['blue_team_2'],
            blue_team_3 = item['blue_team_3'],
            year = item['year']
        )
        to_add.append(new_entry)
    session.add_all(to_add)
    session.commit()
    logger.info('additional user data written to sql.')

    # get events data
    logger.info('Grabbing events data')
    source = requests.get(f'{Constants.API_ENDPOINT}/get_events_data', {'User': settings_config.get('user', 'auth_key'), 'VersionDictionaryData': 'None'})
    settings_config.set('data', 'events_version', source.headers['VersionEvents'])
    data = json.loads(source.text)
    to_add = []
    for item in data:
        new_entry = models.Event(
            key = item['key'],
            week = item['week'],
            district = item['district'],
            year = item['year']
        )
        to_add.append(new_entry)
    session.add_all(to_add)
    session.commit()
    fill_perm_tables(settings_config.get('model', 'mode'), settings_config.getfloat('model', 'late_weighting'))
    with open('config.ini', 'w') as configfile:
        settings_config.write(configfile)


def fill_perm_tables(mode: str, late_weighting:float) -> None:
    """
    mode: str: -- mode from settings
    late_weighting: float -- late_weighting from settings. 0.0 means no late weighting
    """
    from data_handling.process_data import team_stats_process_full_sql, load_matches_alliance_stats_full_sql, get_basic_filter
    if mode == 'week_by_week':
        processed_weeks = []
        for week in [0,1,2,3,4,5,-1]:
            # processing all of team profile data
            processed_weeks.append(week)
            if week != -1:
                team_stats_process_full_sql('match_expanded_tba', f'teams_profile_week_{week}', get_basic_filter(processed_weeks, 'all'), late_weighting)
            else:
                team_stats_process_full_sql('match_expanded_tba', f'teams_profile_all_weeks', get_basic_filter(processed_weeks, 'all'), late_weighting)
        
        for week in [0,1,2,3,4,5,-1]:
            if week != -1:
                load_matches_alliance_stats_full_sql('match_dictionary', f'teams_profile_week_{week}', f'all_matches_stats_week_{week}', 'events', get_basic_filter([week], 'all'), delete_existing=True)
            else:
                load_matches_alliance_stats_full_sql('match_dictionary', f'teams_profile_all_weeks', f'all_matches_stats_all_weeks', 'events', get_basic_filter([week], 'all'), delete_existing=True)
    elif mode == 'all_at_once':
        team_stats_process_full_sql('match_expanded_tba', 'teams_profile_all_weeks', get_basic_filter('all', 'all'), late_weighting=late_weighting)
        load_matches_alliance_stats_full_sql('match_dictionary', 'teams_profile_all_weeks', 'all_matches_stats_all_weeks', 'events', get_basic_filter('all', 'all'), delete_existing=True)
        logger.debug('setup for all at once completed')
    else:
        raise Exception('bad mode')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    setup_application()