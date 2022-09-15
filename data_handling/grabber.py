import logging
import json
from data_handling import models, session
import requests
from gui.utils import Constants
import configparser

logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.read('config.ini')

def get_header() -> dict: # doing this so its updated throughout running the application
    """
    Function to use internally to get an updated header
    """
    config.read('config.ini')
    header = {'User': config.getint('user', 'auth_key'),
    'VersionDictionaryData': config.getint('data', 'dictionary_version'), 
    'VersionUserSubmittedData': config.getint('data', 'user_extra_version'),
    'VersionEvents': config.getint('data', 'events_version'),
    'CurrentVersion': config.get('version', 'version_number')}
    return header

def get_expanded_match_data() -> None:
    """
    Method that is used to get the match data from the API
    """
    logger.info('Getting TBA data from api')
    source = requests.get(f'{Constants.API_ENDPOINT}/get_match_data', get_header())
    data = json.loads(source.text)
    config.set('data', 'tba_version', source.headers['VersionTBAData'])
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
    logger.info('TBA data updated.')
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    logger.info('versions updated.')

def get_match_dictionary() -> None:
    """
    Function to get the updated version of the match dictionary from the api
    """
    # grabbing match dictionary data from api
    logger.info('Grabbing match dictionary from api')
    source = requests.get(f'{Constants.API_ENDPOINT}/get_match_dictionary_data', get_header())
    config.set('data', 'dictionary_version', source.headers['VersionDictionaryData'])
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
            winning_alliance = item['winning_alliance'],
            comp_level = item['comp_level'],
            year = item['year']
        )
        to_add.append(new_entry)
    session.add_all(to_add)
    session.commit()
    logger.info('match dictionary data written to sql')
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    logger.info('versions updated.')

def get_user_submitted_data() -> None:
    """
    Function to get user submitted data from the api
    """
    # grabbing user submitted match data from api
    logger.info('Grabbing additional user data from api')
    source = requests.get(f'{Constants.API_ENDPOINT}/get_user_expanded_match_data', get_header())
    config.set('data', 'user_extra_version', source.headers['VersionUserSubmittedData'])
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
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    logger.info('versions updated.')

def get_events_data() -> None:
    """
    Function to get the events data
    """
    # get events data
    logger.info('Grabbing events data')
    source = requests.get(f'{Constants.API_ENDPOINT}/get_events_data', get_header())
    config.set('data', 'events_version', source.headers['VersionEvents'])
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
    logger.info('events data gotten.')
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    logger.info('versions updated.')

