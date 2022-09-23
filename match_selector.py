import pandas as pd
import numpy as np
from utils import Constants
YEAR = 2022
HEADER = {'X-TBA-Auth-Key': Constants.KEY}
EVENT_DATA_FILEPATH = 'about_all_events.json'

def select_by_team(team_list, match_data, returns='indexes'):
    """
    Method that returns the indices of matches in the match data (and the match stats data) that meet the criteria
    team_list -- team to be selected
    match_data -- a pandas DataFrame of uncleaned match data from the api
    """

    # converting single element into iterable
    if (type(team_list) != list) & (type(team_list) != tuple):
        team_list = [team_list]

    # iterating through all teams and grabbing their matches
    all_matches_indexes = []
    for team in team_list:
        blue_matches = np.array(match_data.loc[match_data['alliances'].apply(lambda x: team in x['blue']['team_keys'])].index)
        red_matches = np.array(match_data.loc[match_data['alliances'].apply(lambda x: team in x['red']['team_keys'])].index)
        all_matches_indexes.append(np.concatenate([blue_matches, red_matches]))
    all_matches_indexes = np.concatenate(all_matches_indexes)
    all_matches_indexes = np.unique(all_matches_indexes)
    return list(all_matches_indexes)


def select_by_event(event_list, match_data):
    """
    Method that returns the a list of indices in the match data (and the match stats data) that meet the criteria
    event_list -- list of event keys to select matches from
    match_data -- a pandas DataFrame of uncleaned match data from the api
    """

    # converting single element into iterable
    if (type(event_list) != list) & (type(event_list) != tuple):
        event_list = [event_list]
    
    all_matches_indexes = []
    for event in event_list:
        all_matches_indexes.append(np.array(match_data.loc[match_data['event_key'] == event].index))
    
    return list(np.concatenate(all_matches_indexes))

def select_by_event_type(type_list, match_data):
    """
    Method that returns the indices of matches in the match data (and the match stats data) that meet the criteria
    type_list -- list of strings of the event type. Possible values: "Regional", "District", "District Championship", "Championship Division", "Championship Final"
    match_data -- a pandas DataFrame of uncleaned match data from the api
    """

    #converting single element into iterable
    if (type(type_list) is not list) & (type(type_list) is not tuple):
        type_list = [type_list]

    # getting events with type
    events_data = pd.read_json(EVENT_DATA_FILEPATH)
    events_with_type = []
    for tp in type_list:
        events_with_type.append(np.array(events_data.loc[events_data['event_type_string'] == tp]['key']))
    events_with_type = list(np.concatenate(events_with_type))
    return select_by_event(events_with_type, match_data)

def select_by_event_district(district_list, match_data):
    """
    Method that returns the indices of matches in the match data (and the match stats data) that meet the criteria
    district_list-- list of district keys whose matches are to be selected
    match_data -- a pandas DataFrame of uncleaned match data from the api
    """

    #converting single element into iterable
    if (type(district_list) != list) & (type(district_list) != tuple):
        district_list = [district_list]

    def in_district(x, district):
        try:
            return x['key'] == district
        except:
            return False

    # getting events in district
    events_data = pd.read_json(EVENT_DATA_FILEPATH)
    events_in_all_districts = []
    for district in district_list:
        events_in_district = np.array(events_data.loc[events_data['district'].apply(lambda x: in_district(x, district))]['key'])
        events_in_all_districts.append(events_in_district)
    try:
        events_in_all_districts = list(np.concatenate(events_in_all_districts))
    except:
        return []
    return select_by_event(events_in_all_districts, match_data)

def select_by_event_week(week_list, match_data):
    """
    Method that returns the indices of matches in the match data (and the match stats data) that meet the criteria
    type_list -- list of numbers for event type
    match_data -- a pandas DataFrame of uncleaned match data from the api
    """

    if (type(week_list) != list) & (type(week_list) != tuple):
        week_list = [week_list]
    
    events_data = pd.read_json(EVENT_DATA_FILEPATH)
    events_with_type = []
    for week in week_list:
        if week != -1:
            events_with_type.append(np.array(events_data.loc[events_data['week'] == week]['key']))
        else:
            events_with_type.append(np.array(events_data.loc[events_data['week'].apply(lambda x: x not in [0,1,2,3,4,5])]['key']))

    events_with_type = list(np.concatenate(events_with_type))
    return select_by_event(events_with_type, match_data)




if __name__ == '__main__':
    matches_df = pd.read_json('all_matches_uncleaned.json')
    print(select_by_event_week([1, 2], matches_df))