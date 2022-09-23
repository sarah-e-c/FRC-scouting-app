# run this file when running the app for the first time.
import configparser
import secrets
from utils import Constants
import logging
import os
import json

import requests

def setup_application():

    logger = logging.getLogger(__name__)


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

    with open('config.ini', 'w') as configfile:
        settings_config.write(configfile)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    setup_application()