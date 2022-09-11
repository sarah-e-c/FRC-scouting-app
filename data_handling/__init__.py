# setting up sqlalchemy
import os
import logging
import requests
import sqlalchemy
import json
API_HOST = 'http://127.0.0.1:5000/'

logger = logging.getLogger(__name__)
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///data.db')
Base = declarative_base()

from data_handling import models
Session = sessionmaker()

Session.configure(bind=engine)

session = Session()

if not sqlalchemy.inspect(engine).has_table('match_expanded_tba'):
    logger.info('creating database file')
    Base.metadata.create_all(engine)
    data = json.loads(requests.get(f'{API_HOST}get_match_data').text)
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


