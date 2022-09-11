from data_handling import Base
from data_handling import engine
from sqlalchemy import Column, Integer, String


class MatchExpandedTBA(Base):
    """
    Class that has all of the match data from the perpective of each team. 6x larger than Match
    """

    __tablename__ = 'match_expanded_tba'
    index = Column(Integer, primary_key=True)
    team_name = Column(String)
    comp_level = Column(String)
    event_key = Column(String)
    key  = Column(String)
    match_number = Column(Integer)
    set_number = Column(Integer)
    winning_alliance = Column(String)
    team_alliance = Column(String)
    teammate_1 = Column(String)
    teammate_2 = Column(String)
    teammate_3 = Column(String)
    opponent_1 = Column(String)
    opponent_2 = Column(String)
    opponent_3 = Column(String)
    taxied = Column(Integer)
    hang = Column(Integer)
    alliance_auto_cargo_lower = Column(Integer)
    alliance_auto_cargo_upper = Column(Integer)
    alliance_teleop__cargo_lower = Column(Integer)
    alliance_teleop__cargo_upper = Column(Integer)

    # from match_extra_data... TODO
    # team_auto_lower = Column(Integer)
    # team_auto_upper = Column(Integer)
    # team_teleop_lower = Column(Integer)
    # team_teleop_upper = Column(Integer)
    won_game = Column(Integer)
    week = Column(Integer)

