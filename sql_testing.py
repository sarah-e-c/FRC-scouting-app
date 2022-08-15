import sqlite3
from sqlite3 import Error
import logging
import pandas as pd
import numpy as np
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs.txt')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection objecot or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_matches_data_table(conn: sqlite3.Connection):
    """
    create the uncleaned_matches data table.
    conn -- sqlite3.Connection: connection to database
    """
    query = """
    CREATE TABLE IF NOT EXISTS all_matches_uncleaned (
	match_key text PRIMARY KEY,
	red_team_1 text NOT NULL,
	red_team_2 text NOT NULL,
	red_team_3 text NOT NULL,
	red_hang_1 integer NOT NULL,
	red_hang_2 integer NOT NULL,
	red_hang_3 integer NOT NULL,
	red_taxi_1 integer NOT NULL,
	red_taxi_2 integer NOT NULL,
	red_taxi_3 integer NOT NULL,
	red_auto_cargo_lower integer,
	red_auto_cargo_upper integer,
	red_auto_cargo_points integer,
	red_teleop_cargo_lower integer,
	red_teleop_cargo_upper integer,
	red_teleop_cargo_points integer,
	red_foul_count integer,
	red_foul_points integer,
	red_total_score integer,
	blue_team_1 text NOT NULL,
	blue_team_2 text NOT NULL,
	blue_team_3 text NOT NULL,
	blue_hang_1 integer NOT NULL,
	blue_hang_2 integer NOT NULL,
	blue_hang_3 integer NOT NULL,
	blue_taxi_1 integer NOT NULL,
	blue_taxi_2 integer NOT NULL,
	blue_taxi_3 integer NOT NULL,
	blue_auto_cargo_lower integer,
	blue_auto_cargo_upper integer,
	blue_auto_cargo_points integer,
	blue_teleop_cargo_lower integer,
	blue_teleop_cargo_upper integer,
	blue_teleop_cargo_points integer,
	blue_foul_count integer,
	blue_foul_points integer,
	blue_total_score integer,
	comp_level text NULL,
	event_key text NOT NULL,
	event_week integer NOT NULL,
	winning_alliance integer NOT NULL
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
    except Error as e:
        logger.warn(e)
    
    cursor.close()

def fill_matches_data_table(conn: sqlite3.Connection) -> None:
    """
    Method to fill/update the uncleaned matches data table
    """
    df = pd.read_json('all_matches_uncleaned.json')
    events_data = pd.read_json('about_all_events.json')
    new_df = pd.DataFrame()
    bad_events = pd.read_csv('bad_events.csv')
    bad_events_list = np.unique(bad_events['BadEvents'])
    df = df[df['event_key'].apply(lambda x: x not in bad_events_list)]
    none_list = []
    for _ in range(df.shape[0]):
        none_list.append(None)
    new_df['match_key'] = none_list 
    new_df['red_team_1'] = none_list
    new_df['red_team_2'] = none_list
    new_df['red_team_3'] = none_list
    new_df['red_hang_1'] = none_list
    new_df['red_hang_2'] = none_list
    new_df['red_hang_3'] = none_list
    new_df['red_taxi_1'] = none_list
    new_df['red_taxi_2'] = none_list
    new_df['red_taxi_3'] = none_list
    new_df['red_auto_cargo_lower'] = none_list
    new_df['red_auto_cargo_upper'] = none_list
    new_df['red_auto_cargo_points'] = none_list
    new_df['red_teleop_cargo_lower'] = none_list
    new_df['red_teleop_cargo_upper'] = none_list
    new_df['red_teleop_cargo_points'] = none_list
    new_df['red_foul_count'] = none_list
    new_df['red_foul_points'] = none_list
    new_df['red_total_score'] = none_list
    new_df['blue_team_1'] = none_list
    new_df['blue_team_2'] = none_list
    new_df['blue_team_3'] = none_list
    new_df['blue_hang_1'] = none_list
    new_df['blue_hang_2'] = none_list
    new_df['blue_hang_3'] = none_list
    new_df['blue_taxi_1'] = none_list
    new_df['blue_taxi_2'] = none_list
    new_df['blue_taxi_3'] = none_list
    new_df['blue_auto_cargo_lower'] = none_list
    new_df['blue_auto_cargo_upper'] = none_list
    new_df['blue_auto_cargo_points'] = none_list
    new_df['blue_teleop_cargo_lower'] = none_list
    new_df['blue_teleop_cargo_upper'] = none_list
    new_df['blue_teleop_cargo_points'] = none_list
    new_df['blue_foul_count'] = none_list
    new_df['blue_foul_points'] = none_list
    new_df['blue_total_score'] = none_list
    new_df['comp_level'] = none_list
    new_df['event_key'] = none_list
    new_df['event_week'] = none_list
    new_df['winning_alliance'] = none_list

    logger.debug('data update initialized')

    new_df['match_key'] = df['key']
    for index, row in df.iterrows():
        new_df['red_team_1'].iloc[index] = row['alliances']['red']['team_keys'][0]
        new_df['red_team_2'].iloc[index] = row['alliances']['red']['team_keys'][1]
        new_df['red_team_3'].iloc[index] = row['alliances']['red']['team_keys'][2]
        new_df['red_hang_1'].iloc[index] = row['score_breakdown']['red']['endgameRobot1']
        new_df['red_hang_2'].iloc[index] = row['score_breakdown']['red']['endgameRobot2']
        new_df['red_hang_3'].iloc[index] = row['score_breakdown']['red']['endgameRobot3']
        new_df['red_taxi_1'].iloc[index] = row['score_breakdown']['red']['taxiRobot1']
        new_df['red_taxi_2'].iloc[index] = row['score_breakdown']['red']['taxiRobot2']
        new_df['red_taxi_3'].iloc[index] = row['score_breakdown']['red']['taxiRobot3']
        try:
            new_df['red_auto_cargo_lower'].iloc[index] = row['score_breakdown']['red']['autoCargoLowerBlue'] + row['score_breakdown']['red']['autoCargoLowerRed'] + row['score_breakdown']['red']['autoCargoLowerFar'] + row['score_breakdown']['red']['autoCargoLowerNear']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['red_auto_cargo_lower'].iloc[index] = 0
        try:
            new_df['red_auto_cargo_upper'].iloc[index] = row['score_breakdown']['red']['autoCargoUpperBlue'] + row['score_breakdown']['red']['autoCargoUpperRed'] + row['score_breakdown']['red']['autoCargoUpperFar'] + row['score_breakdown']['red']['autoCargoUpperNear']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['red_auto_cargo_upper'].iloc[index] = 0
        new_df['red_auto_cargo_points'].iloc[index] = row['score_breakdown']['red']['autoCargoPoints']
        try:
            new_df['red_teleop_cargo_lower'].iloc[index] = row['score_breakdown']['red']['teleopCargoLowerFar'] + row['score_breakdown']['red']['teleopCargoLowerBlue'] + row['score_breakdown']['red']['teleopCargoLowerRed'] + row['score_breakdown']['red']['teleopCargoLowerNear']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['red_teleop_cargo_lower'].iloc[index] = 0
        try:
            new_df['red_teleop_cargo_upper'].iloc[index] = row['score_breakdown']['red']['teleopCargoUpperFar'] + row['score_breakdown']['red']['teleopCargoUpperBlue'] + row['score_breakdown']['red']['teleopCargoUpperRed'] + row['score_breakdown']['red']['teleopCargoUpperNear']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['red_teleop_cargo_upper'].iloc[index] = 0
        new_df['red_teleop_cargo_points'].iloc[index] = row['score_breakdown']['red']['teleopPoints']
        try:
            new_df['red_foul_count'].iloc[index] = row['score_breakdown']['red']['foulCount']
            new_df['red_foul_points'].iloc[index] = row['score_breakdown']['red']['foulPoints']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['red_foul_count'].iloc[index] = 0
            new_df['red_foul_points'].iloc[index] = 0
        new_df['red_total_score'].iloc[index] = row['score_breakdown']['red']['totalPoints']
        new_df['blue_team_1'].iloc[index] = row['alliances']['blue']['team_keys'][0]
        new_df['blue_team_2'].iloc[index] = row['alliances']['blue']['team_keys'][1]
        new_df['blue_team_3'].iloc[index] = row['alliances']['blue']['team_keys'][2]
        new_df['blue_hang_1'].iloc[index] = row['score_breakdown']['blue']['endgameRobot1']
        new_df['blue_hang_2'].iloc[index] = row['score_breakdown']['blue']['endgameRobot2']
        new_df['blue_hang_3'].iloc[index] = row['score_breakdown']['blue']['endgameRobot3']
        new_df['blue_taxi_1'].iloc[index] = row['score_breakdown']['blue']['taxiRobot1']
        new_df['blue_taxi_2'].iloc[index] = row['score_breakdown']['blue']['taxiRobot2']
        new_df['blue_taxi_3'].iloc[index] = row['score_breakdown']['blue']['taxiRobot3']
        try:
            new_df['blue_auto_cargo_lower'].iloc[index] = row['score_breakdown']['blue']['autoCargoLowerBlue'] + row['score_breakdown']['blue']['autoCargoLowerRed'] + row['score_breakdown']['blue']['autoCargoLowerFar'] + row['score_breakdown']['blue']['autoCargoLowerNear']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['blue_auto_cargo_lower'].iloc[index] = 0
        try:
            new_df['blue_auto_cargo_upper'].iloc[index] = row['score_breakdown']['blue']['autoCargoUpperBlue'] + row['score_breakdown']['blue']['autoCargoUpperRed'] + row['score_breakdown']['blue']['autoCargoUpperFar'] + row['score_breakdown']['blue']['autoCargoUpperNear']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['blue_auto_cargo_upper'].iloc[index] = 0
        new_df['blue_auto_cargo_points'].iloc[index] = row['score_breakdown']['blue']['autoCargoPoints']

        try:
            new_df['blue_teleop_cargo_lower'].iloc[index] = row['score_breakdown']['blue']['teleopCargoLowerFar'] + row['score_breakdown']['blue']['teleopCargoLowerBlue'] + row['score_breakdown']['blue']['teleopCargoLowerRed'] + row['score_breakdown']['blue']['teleopCargoLowerNear']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['blue_teleop_cargo_lower'].iloc[index] = 0
        try:
            new_df['blue_teleop_cargo_upper'].iloc[index] = row['score_breakdown']['blue']['teleopCargoUpperFar'] + row['score_breakdown']['blue']['teleopCargoUpperBlue'] + row['score_breakdown']['blue']['teleopCargoUpperRed'] + row['score_breakdown']['blue']['teleopCargoUpperNear']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['blue_teleop_cargo_upper'].iloc[index] = 0
        new_df['blue_teleop_cargo_points'].iloc[index] = row['score_breakdown']['blue']['teleopPoints']
        try:
            new_df['blue_foul_count'].iloc[index] = row['score_breakdown']['blue']['foulCount']
            new_df['blue_foul_points'].iloc[index] = row['score_breakdown']['blue']['foulPoints']
        except Exception as e:
            logger.warning(f'Error in row {row}: {e}')
            new_df['blue_foul_count'].iloc[index] = 0
            new_df['blue_foul_points'].iloc[index] = 0
        new_df['blue_total_score'].iloc[index] = row['score_breakdown']['blue']['totalPoints']

    logging.debug('Finished loading into a dataframe')
    new_df['event_key'] = df['event_key']
    def get_week(event_key):
        week = events_data.loc[events_data['key'] == event_key].iloc[0]['week']
        if week in range(6):
            return week
        else:
            return -1
    
    new_df['blue_hang_1'] = new_df['blue_hang_1'].map({np.nan: 0, '': 0, None: 0, 'Low': 1, 'Mid': 2, 'Traversal': 3, 'High':4})
    new_df['blue_hang_2'] = new_df['blue_hang_2'].map({np.nan: 0, '': 0, None: 0, 'Low': 1, 'Mid': 2, 'Traversal': 3, 'High':4})
    new_df['blue_hang_3'] = new_df['blue_hang_3'].map({np.nan: 0, '': 0, None: 0, 'Low': 1, 'Mid': 2, 'Traversal': 3, 'High':4})

    new_df['red_hang_1'] = new_df['red_hang_1'].map({np.nan: 0, '': 0, None: 0, 'Low': 1, 'Mid': 2, 'Traversal': 3, 'High':4})
    new_df['red_hang_2'] = new_df['red_hang_2'].map({np.nan: 0, '': 0, None: 0, 'Low': 1, 'Mid': 2, 'Traversal': 3, 'High':4})
    new_df['red_hang_3'] = new_df['red_hang_3'].map({np.nan: 0, '': 0, None: 0, 'Low': 1, 'Mid': 2, 'Traversal': 3, 'High':4})

    new_df['blue_hang_1'].fillna(0, inplace=True)
    new_df['blue_hang_2'].fillna(0, inplace=True)
    new_df['blue_hang_3'].fillna(0, inplace=True)
    new_df['red_hang_1'].fillna(0, inplace=True)
    new_df['red_hang_2'].fillna(0, inplace=True)
    new_df['red_hang_3'].fillna(0, inplace=True)


    yes_no_mapping = {'Yes': 1, 'No': 0, np.nan: 0, '': 0}
    new_df['blue_taxi_1'] = new_df['blue_taxi_1'].map(yes_no_mapping)
    new_df['blue_taxi_2'] = new_df['blue_taxi_2'].map(yes_no_mapping)
    new_df['blue_taxi_3'] = new_df['blue_taxi_3'].map(yes_no_mapping)
    new_df['red_taxi_1'] = new_df['red_taxi_1'].map(yes_no_mapping)
    new_df['red_taxi_2'] = new_df['red_taxi_2'].map(yes_no_mapping)
    new_df['red_taxi_3'] = new_df['red_taxi_3'].map(yes_no_mapping)

    new_df['blue_taxi_1'].fillna(0, inplace=True)
    new_df['blue_taxi_2'].fillna(0, inplace=True)
    new_df['blue_taxi_3'].fillna(0, inplace=True)
    new_df['red_taxi_1'].fillna(0, inplace=True)
    new_df['red_taxi_2'].fillna(0, inplace=True)
    new_df['red_taxi_3'].fillna(0, inplace=True)
    
    new_df['event_week'] = new_df['event_key'].apply(get_week)
    new_df['comp_level'] = df['comp_level'].map({'qm':0, 'qf': 1, 'sf': 2, 'f': 3, 'ef': 4})
    new_df['winning_alliance'] = df['winning_alliance'].map({'red': 1, 'blue': -1}).fillna(0)
    new_df = new_df.values.tolist()
    content = new_df # 41 different columns
    query = """
    INSERT INTO all_matches_uncleaned
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    cursor = conn.cursor()
    try:
        cursor.executemany(query, content)
        logging.info(f"{cursor.rowcount} rows inserted.")
    except Error as e:
        logging.warning(e)
    conn.commit()
    conn.close()

def create_about_all_events_table(conn: sqlite3.Connection):
    query = """
    CREATE TABLE IF NOT EXISTS about_all_events(
        key text PRIMARY KEY,
        district text,
        type text,
        week integer,
        year integer
    )
    """
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()

def fill_about_all_events_table(conn: sqlite3.Connection, path='about_all_events.json'):
    """
    method to fill/update about_all_events table in database.
    conn: sqlite3.Connection to database
    path -- string path or pandas df with data from the api
    """
    query = """
    INSERT INTO about_all_events
    VALUES (?,?,?,?,?)
    """

    if type(path) == str:
        df = pd.read_csv(path)
    else:
        df = path
    
    new_df = pd.DataFrame()
    new_df['key'] = df['key']
    new_df['district'] = df['district']
    new_df['type'] = df['event_type_string']
    new_df['week'] = df['week']
    new_df['year'] = df['year']
    
    cursor = conn.cursor()
    cursor.executemany(query, new_df.values.tolist())

    
if __name__ == '__main__':
    database = r"sql_data.db"
    connection = create_connection(database)
    create_matches_data_table(connection)
    fill_matches_data_table(connection)

    # df = pd.read_json('all_matches_uncleaned.json')
    # print(df)
    # df.to_sql('all_uncleaned_matches', connection, if_exists='replace')
    # # cursor = connection.cursor()
    # # cursor.close()
    # connection.close()