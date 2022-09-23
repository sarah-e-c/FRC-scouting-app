from data_handling import Base
from data_handling import engine
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship


class MatchDictionary(Base):
    """
    Model for the match_dictionary table
    """
    __tablename__ = 'match_dictionary'
    key = Column(String, primary_key=True)
    red_team_1 = Column(String)
    red_team_2 = Column(String)
    red_team_3 = Column(String)
    blue_team_1 = Column(String)
    blue_team_2 = Column(String)
    blue_team_3 = Column(String)
    year = Column(Integer)
    occurred = Column(Integer)
    event_key = Column(String, ForeignKey('events.key'))
    comp_level = Column(String)
    winning_alliance = Column(String, nullable=True)
    event = relationship('Event', back_populates='matches')
    extra_data = relationship('MatchExtraData', back_populates='dictionary_entry')
    tba_data = relationship('MatchExpandedTBA', back_populates='dictionary_entry')

class Event(Base): 
    __tablename__ = 'events'
    key = Column(String, primary_key=True)
    week = Column(Integer)
    year = Column(Integer)
    matches = relationship('MatchDictionary', back_populates='event')
    district = Column(String)
    
class MatchExtraData(Base):
    __tablename__ = 'match_extra_data'
    index = Column(Integer, primary_key=True)
    key = Column(String, ForeignKey('match_dictionary.key'))
    key_tba = Column(String, ForeignKey('match_expanded_tba.key'))
    dictionary_entry = relationship('MatchDictionary', back_populates='extra_data')
    team_name = Column(String)
    match_number = Column(Integer)
    team_auto_lower = Column(Integer)
    team_auto_upper = Column(Integer)
    team_teleop_lower = Column(Integer)
    team_teleop_upper = Column(Integer)
    tba_data = relationship('MatchExpandedTBA', back_populates='extra_data')

class MatchExpandedTBA(Base):
    """
    Class that has all of the match data from the perpective of each team. 6x larger than Match
    """

    __tablename__ = 'match_expanded_tba'
    index = Column(Integer, primary_key=True)
    team_name = Column(String)
    comp_level = Column(String)
    event_key = Column(String)
    key  = Column(String, ForeignKey('match_dictionary.key'))
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
    dictionary_entry = relationship('MatchDictionary', back_populates='tba_data')
    extra_data = relationship('MatchExtraData', back_populates='tba_data')


class TeamsProfileAllWeeks(Base):
    """
    represents the table of the meta stats of the teams calculated from all available weeks
    """
    __tablename__ = 'teams_profile_all_weeks'
    team_name = Column(String, primary_key=True)
    win_rate = Column(Float)
    team_auto_lower = Column(Float)
    team_auto_upper = Column(Float)
    team_teleop_lower = Column(Float)
    team_teleop_upper = Column(Float)
    hang_score = Column(Float)
    highest_comp_level = Column(Integer)

class TeamsProfileWeek0(Base):
    """
    represents the table of the meta stats of the teams calculated from first through fifth weeks
    """
    __tablename__ = 'teams_profile_week_0'
    team_name = Column(String, primary_key=True)
    win_rate = Column(Float)
    team_auto_lower = Column(Float)
    team_auto_upper = Column(Float)
    team_teleop_lower = Column(Float)
    team_teleop_upper = Column(Float)
    hang_score = Column(Float)
    highest_comp_level = Column(Integer)

class TeamsProfileWeek1(Base):
    """
    represents the table of the meta stats of the teams calculated from first week
    """
    __tablename__ = 'teams_profile_week_1'
    team_name = Column(String, primary_key=True)
    win_rate = Column(Float)
    team_auto_lower = Column(Float)
    team_auto_upper = Column(Float)
    team_teleop_lower = Column(Float)
    team_teleop_upper = Column(Float)
    hang_score = Column(Float)
    highest_comp_level = Column(Integer)

class TeamsProfileWeek2(Base):
    """
    represents the table of the meta stats of the teams calculated from first and second weeks
    """
    __tablename__ = 'teams_profile_week_2'
    team_name = Column(String, primary_key=True)
    win_rate = Column(Float)
    team_auto_lower = Column(Float)
    team_auto_upper = Column(Float)
    team_teleop_lower = Column(Float)
    team_teleop_upper = Column(Float)
    hang_score = Column(Float)
    highest_comp_level = Column(Integer)

class TeamsProfileWeek3(Base):
    """
    represents the table of the meta stats of the teams calculated from first through third weeks
    """
    __tablename__ = 'teams_profile_week_3'
    team_name = Column(String, primary_key=True)
    win_rate = Column(Float)
    team_auto_lower = Column(Float)
    team_auto_upper = Column(Float)
    team_teleop_lower = Column(Float)
    team_teleop_upper = Column(Float)
    hang_score = Column(Float)
    highest_comp_level = Column(Integer)

class TeamsProfileWeek4(Base):
    """
    represents the table of the meta stats of the teams calculated from first through fourth weeks
    """
    __tablename__ = 'teams_profile_week_4'
    team_name = Column(String, primary_key=True)
    win_rate = Column(Float)
    team_auto_lower = Column(Float)
    team_auto_upper = Column(Float)
    team_teleop_lower = Column(Float)
    team_teleop_upper = Column(Float)
    hang_score = Column(Float)
    highest_comp_level = Column(Integer)

class TeamsProfileWeek5(Base):
    """
    represents the table of the meta stats of the teams calculated from first through fifth weeks
    """
    __tablename__ = 'teams_profile_week_5'
    team_name = Column(String, primary_key=True)
    win_rate = Column(Float)
    team_auto_lower = Column(Float)
    team_auto_upper = Column(Float)
    team_teleop_lower = Column(Float)
    team_teleop_upper = Column(Float)
    hang_score = Column(Float)
    highest_comp_level = Column(Integer)


class AllMatchesStatsAllWeeks(Base):
    """
    represents the table of all matches' stats for training data
    """
    __tablename__ = 'all_matches_stats_all_weeks'
    key = Column(String, primary_key=True)
    avg_winrate = Column(Float)
    highest_avg_winrate = Column(Float)
    lowest_avg_winrate = Column(Float)
    avg_auto_lower = Column(Float)
    highest_auto_lower = Column(Float)
    avg_auto_upper = Column(Float)
    highest_auto_upper = Column(Float)
    avg_teleop_lower = Column(Float)
    highest_teleop_lower = Column(Float)
    avg_teleop_upper = Column(Float)
    highest_teleop_upper = Column(Float)
    lowest_teleop_upper = Column(Float)
    avg_hang_score = Column(Float)
    avg_highest_comp_level = Column(Float)
    event_key = Column(String)
    winning_alliance = Column(Integer)

class AllMatchesStatsWeek0(Base):
    """
    represents the table of all matches' stats just for week 0 for training data
    """
    __tablename__ = 'all_matches_stats_week_0'
    key = Column(String, primary_key=True)
    avg_winrate = Column(Float)
    highest_avg_winrate = Column(Float)
    lowest_avg_winrate = Column(Float)
    avg_auto_lower = Column(Float)
    highest_auto_lower = Column(Float)
    avg_auto_upper = Column(Float)
    highest_auto_upper = Column(Float)
    avg_teleop_lower = Column(Float)
    highest_teleop_lower = Column(Float)
    avg_teleop_upper = Column(Float)
    highest_teleop_upper = Column(Float)
    lowest_teleop_upper = Column(Float)
    avg_hang_score = Column(Float)
    avg_highest_comp_level = Column(Float)
    event_key = Column(String)
    winning_alliance = Column(Integer)

class AllMatchesStatsWeek1(Base):
    """
    represents the table of all matches' stats calcluated just for week 1 for training data
    """
    __tablename__ = 'all_matches_stats_week_1'
    key = Column(String, primary_key=True)
    avg_winrate = Column(Float)
    highest_avg_winrate = Column(Float)
    lowest_avg_winrate = Column(Float)
    avg_auto_lower = Column(Float)
    highest_auto_lower = Column(Float)
    avg_auto_upper = Column(Float)
    highest_auto_upper = Column(Float)
    avg_teleop_lower = Column(Float)
    highest_teleop_lower = Column(Float)
    avg_teleop_upper = Column(Float)
    highest_teleop_upper = Column(Float)
    lowest_teleop_upper = Column(Float)
    avg_hang_score = Column(Float)
    avg_highest_comp_level = Column(Float)
    event_key = Column(String)
    winning_alliance = Column(Integer)

class AllMatchesStatsWeek2(Base):
    """
    represents the table of all matches' stats just from week 1 and 2 for training data
    """
    __tablename__ = 'all_matches_stats_week_2'
    key = Column(String, primary_key=True)
    avg_winrate = Column(Float)
    highest_avg_winrate = Column(Float)
    lowest_avg_winrate = Column(Float)
    avg_auto_lower = Column(Float)
    highest_auto_lower = Column(Float)
    avg_auto_upper = Column(Float)
    highest_auto_upper = Column(Float)
    avg_teleop_lower = Column(Float)
    highest_teleop_lower = Column(Float)
    avg_teleop_upper = Column(Float)
    highest_teleop_upper = Column(Float)
    lowest_teleop_upper = Column(Float)
    avg_hang_score = Column(Float)
    avg_highest_comp_level = Column(Float)
    event_key = Column(String)
    winning_alliance = Column(Integer)

class AllMatchesStatsWeek3(Base):
    """
    represents the table of all matches' stats just from week 1 through 3 for training data
    """
    __tablename__ = 'all_matches_stats_week_3'
    key = Column(String, primary_key=True)
    avg_winrate = Column(Float)
    highest_avg_winrate = Column(Float)
    lowest_avg_winrate = Column(Float)
    avg_auto_lower = Column(Float)
    highest_auto_lower = Column(Float)
    avg_auto_upper = Column(Float)
    highest_auto_upper = Column(Float)
    avg_teleop_lower = Column(Float)
    highest_teleop_lower = Column(Float)
    avg_teleop_upper = Column(Float)
    highest_teleop_upper = Column(Float)
    lowest_teleop_upper = Column(Float)
    avg_hang_score = Column(Float)
    avg_highest_comp_level = Column(Float)
    event_key = Column(String)
    winning_alliance = Column(Integer)

class AllMatchesStatsWeek4(Base):
    """
    represents the table of all matches' stats just from week 1 through 4 for training data
    """
    __tablename__ = 'all_matches_stats_week_4'
    key = Column(String, primary_key=True)
    avg_winrate = Column(Float)
    highest_avg_winrate = Column(Float)
    lowest_avg_winrate = Column(Float)
    avg_auto_lower = Column(Float)
    highest_auto_lower = Column(Float)
    avg_auto_upper = Column(Float)
    highest_auto_upper = Column(Float)
    avg_teleop_lower = Column(Float)
    highest_teleop_lower = Column(Float)
    avg_teleop_upper = Column(Float)
    highest_teleop_upper = Column(Float)
    lowest_teleop_upper = Column(Float)
    avg_hang_score = Column(Float)
    avg_highest_comp_level = Column(Float)
    event_key = Column(String)
    winning_alliance = Column(Integer)

class AllMatchesStatsWeek5(Base):
    """
    represents the table of all matches' stats just from week 1 through 5 for training data
    """
    __tablename__ = 'all_matches_stats_week_5'
    key = Column(String, primary_key=True)
    avg_winrate = Column(Float)
    highest_avg_winrate = Column(Float)
    lowest_avg_winrate = Column(Float)
    avg_auto_lower = Column(Float)
    highest_auto_lower = Column(Float)
    avg_auto_upper = Column(Float)
    highest_auto_upper = Column(Float)
    avg_teleop_lower = Column(Float)
    highest_teleop_lower = Column(Float)
    avg_teleop_upper = Column(Float)
    highest_teleop_upper = Column(Float)
    lowest_teleop_upper = Column(Float)
    avg_hang_score = Column(Float)
    avg_highest_comp_level = Column(Float)
    event_key = Column(String)
    winning_alliance = Column(Integer)

table_name_to_model = {
    'match_dictionary': MatchDictionary,
    'events': Event,
    'match_extra_data': MatchExtraData,
    'match_expanded_tba': MatchExpandedTBA,
    'teams_profile_all_weeks': TeamsProfileAllWeeks,
    'teams_profile_week_0': TeamsProfileWeek0,
    'teams_profile_week_1': TeamsProfileWeek1,
    'teams_profile_week_2': TeamsProfileWeek2,
    'teams_profile_week_3': TeamsProfileWeek3,
    'teams_profile_week_4': TeamsProfileWeek4,
    'teams_profile_week_5': TeamsProfileWeek5,
    'all_matches_stats_all_weeks': AllMatchesStatsAllWeeks,
    'all_matches_stats_week_0': AllMatchesStatsWeek0,
    'all_matches_stats_week_1': AllMatchesStatsWeek1,
    'all_matches_stats_week_2': AllMatchesStatsWeek2,
    'all_matches_stats_week_3': AllMatchesStatsWeek3,
    'all_matches_stats_week_4': AllMatchesStatsWeek4,
    'all_matches_stats_week_5': AllMatchesStatsWeek5
}