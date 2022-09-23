import pandas as pd
from xgboost import XGBClassifier
import match_selector as selector
import data_setup as setup
import optuna
import os
from sklearn.metrics import accuracy_score
import logging
from data_handling import models, session, engine
from sqlalchemy import String, Integer, Float


logger = logging.getLogger(__name__)
class FRCModel():
    """
    Class to be used like sklearn-like ML model. Has features specific to the data.
    """
    def __init__(self, model='XGBoost', mode='files', teams_directory='teams_data', late_weighting=False, event_data_filepath='about_all_events.json', enable_sql=True):
        """
        model='XGBoost' -- either supported string or other model that supports fit() and transform()
        mode- 'files' -- supported modes
        teams_directory='teams_data' -- directory where the teams are held
        late_weighting=False -- value for experimental late weighting for teams 
        """
        self.enable_sql = enable_sql

        if not enable_sql:
            self.event_data_filepath = event_data_filepath
        else:
            self.event_data_filepath = 'sql'

        self.mode = mode

        if late_weighting < 0.05:
            self.late_weighting = False
        else:
            self.late_weighting = late_weighting

        # list of supported models
        if model =='XGBoost':
            self.model = XGBClassifier()
        else:
            self.model = model

        
        # modes
        if mode=='files':
            self.teams_directory = teams_directory
        
        self.teams_directory = teams_directory

        logger.debug(f'FRCModel created. params:\n event data filepath: {event_data_filepath},\n mode: {self.mode}\n, late weighting: {self.late_weighting}, \n model: {type(self.model)}')
        

    def fit(self, X=False, y=False, included_weeks=[], data_preloaded_filepath=False, matches_data_preloaded_filepath=False, write_data=False):
        """
        \b
        |  method to fit the model. Calls the model's fit method. \n
        |  PARAMETERS
        |  ----------
        |
        |  mode='default': 'default' - pass in X and y to directly fit the model, 'week_by_week' to use the files to load separate team stats for each week \n
        |  X=False: pass False if using file mode, but pass pandas DataFrame if using default method (an error will be thrown if not) \n
        |  y=False: pass False if using file mode, but pass pandas Series if using default method (an error will be thrown if not) \n
        |  included_weeks=[]: pass a list to select which weeks to include (use -1 last), or pass 'all' to get all of the weeks \n
        |  data_preloaded_filepath: pass a string of the first folders in order for the data to not be processed and instead read. \n
        |  write_data: pass True to write the processed data to csv files.
        """


        if included_weeks == 'all':
            included_weeks = [0,1,2,3,4,5,-1] # all weeks represented
        elif type(included_weeks) == str:
            included_weeks = eval(included_weeks)

        # incomplete default files mode
        if self.mode == 'files':
            pass

            # setup.team_stats_process(late_weighting=False)
        
        #week by week mode: evaluating team stats based on data evaluated weekly (recommended)
        #WARNING: this mode is currently very time intensive and needs to be optomized
        elif self.mode == 'week_by_week':
            if not self.enable_sql:
                logger.debug(f'Starting model fit in week by week mode. Fit weeks: {included_weeks}, Data preloaded: {data_preloaded_filepath}')
                all_events = pd.read_json(self.event_data_filepath)
                
                #user passed False
                if not data_preloaded_filepath:
                    weeks_processed = []
                    weeks_dfs = []
                    for week in included_weeks:
                        weeks_processed.append(week)
                        weeks_dfs.append(setup.team_stats_process(team_stats_filepath=False, included_weeks=weeks_processed, late_weighting=self.late_weighting, verbose=False, sql_mode=self.enable_sql))
                    
                    #write data just processed to csv for faster testing/use
                    if write_data:
                        for df, week in zip(weeks_dfs, included_weeks):
                            df.to_csv(f'old code/data/match_data_by_cum_week/week-{week}-data')
                    logger.debug('Finished generating weekly stats sheets.')
                # user passed directory
                else:
                    weeks_dfs=[]
                    for file in os.scandir(f'{data_preloaded_filepath}/cumulative_week_data'):
                        weeks_dfs.append(pd.read_csv(file))
                

                # calculating averages 
                all_matches_weekly_list = []
                if not data_preloaded_filepath:
                    for index, week in enumerate(included_weeks):
                        if week != -1:
                            all_matches_weekly_list.append(setup.load_matches_alliance_stats(team_stats_filepath=weeks_dfs[index], event_keys=all_events.loc[all_events['week'] == week]['key'], verbose=True, all_matches_stats_filepath=False, enable_sql=self.enable_sql))
                        else: 
                            all_matches_weekly_list.append(setup.load_matches_alliance_stats(team_stats_filepath=weeks_dfs[index], event_keys=all_events.loc[all_events['week'].apply(lambda x: x not in [0,1,2,3,4,5])]['key'], verbose=True, all_matches_stats_filepath=False, enable_sql=self.enable_sql))
                    if write_data:
                        for df, week in zip(all_matches_weekly_list, included_weeks):
                            df.to_csv(f'old code/data/match_data_by_cum_week/week_{week}_match_data')
                    logger.debug('Finished generating match specific data sheets.')
                else:
                    for file in os.scandir(f'{data_preloaded_filepath}/match_data_by_cum_week'):
                        all_matches_weekly_list.append(pd.read_csv(file))
                
                #combining all of the matches into one DataFrame based on the week that they occurred

                #returning a single DataFrame with all matches
                completed_data = []
                for index, week in enumerate(included_weeks):
                    #print(len(all_matches_weekly_list), 'dfs')
                    #print(included_weeks)
                    completed_data.append(all_matches_weekly_list[index].iloc[selector.select_by_event_week([week], all_matches_weekly_list[index])])
                
                self.X = pd.concat(completed_data)
                self.X.pop('event_key')
                self.X.pop('Unnamed: 0')
                
                self.y = self.X.pop('winning_alliance')
                self.y = self.y.map(lambda x: x+1)
                
                try:
                    self.model.fit(self.X,self.y)
                except Exception as e:
                    logger.exception('Something went wrong fitting data.')
                    raise e

                
            elif self.enable_sql:
                all_events = pd.read_sql('events', engine)
                logger.debug(f'Starting model fit in week by week mode. Fit weeks: {included_weeks}, Data preloaded: {data_preloaded_filepath} SQL mode: {self.enable_sql}')
                
                #user passed False
                if not data_preloaded_filepath:
                    weeks_processed = []
                    weeks_dfs = []
                    for week in included_weeks:
                        weeks_processed.append(week)
                        weeks_dfs.append(setup.team_stats_process(team_stats_filepath=False, included_weeks=weeks_processed, late_weighting=self.late_weighting, verbose=False, directory='match_expanded_tba', sql_mode=self.enable_sql))
                    
                    #write data just processed to csv for faster testing/use
                    if write_data:
                        for df, week in zip(weeks_dfs, included_weeks):
                            if week == -1:
                                table_name = 'teams_profile_all_weeks' # may be problematic
                            else:
                                table_name = f'teams_profile_week_{week}'
                            df.rename({'TeamName': 'team_name',
                                'WinRate': 'win_rate',
                                'TeamAutoLower': 'team_auto_lower',
                                'TeamAutoUpper': 'team_auto_upper',
                                'TeamTeleopLower': 'team_teleop_lower',
                                'TeamTeleopUpper': 'team_teleop_upper',
                                'HangScore': 'hang_score',
                                'HighestCompLevel': 'highest_comp_level'}, inplace=True, axis='columns')
                            df.to_sql(table_name, engine,
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
                    logger.debug('Finished generating weekly stats sheets.')
                # user passed directory
                else:
                    
                    weeks_dfs=[]
                    for week in included_weeks:
                        if week == -1:
                            table_name = 'teams_profile_all_weeks' # may be problematic
                        else:
                            table_name = f'teams_profile_week_{week}'
                        weeks_dfs.append(pd.read_sql(table_name, engine))
                
                # calculating averages 
                all_matches_weekly_list = []

                if not matches_data_preloaded_filepath:
                    for index, week in enumerate(included_weeks):
                        if week != -1:
                            setup.load_matches_alliance_stats(team_stats_filepath=weeks_dfs[index], event_keys=list(all_events.loc[all_events['week'] == week]['key']), verbose=True, all_matches_stats_filepath=f'all_matches_stats_week_{week}', enable_sql=True, all_matches_filepath='match_dictionary')
                        else:
                            setup.load_matches_alliance_stats(team_stats_filepath=weeks_dfs[index], event_keys=list(all_events.loc[all_events['week'].apply(lambda x: x not in [0,1,2,3,4,5])]['key']), verbose=True, all_matches_stats_filepath='all_matches_stats_all_weeks', enable_sql=True, all_matches_filepath='match_dictionary')
                    if write_data:
                        for df, week in zip(all_matches_weekly_list, included_weeks):
                            if week == -1:
                                table_name = 'all_matches_stats_all_weeks'
                            else:
                                table_name = f'all_matches_stats_week_{week}'
                            #df.to_sql(table_name, engine)
                    logger.debug('Finished generating match specific data sheets.')

                for week in included_weeks:
                    if week == -1:
                        table_name = 'all_matches_stats_all_weeks'
                    else:
                        table_name = f'all_matches_stats_week_{week}'
                    all_matches_weekly_list.append(pd.read_sql(table_name, engine))
                
                #combining all of the matches into one DataFrame based on the week that they occurred

                #returning a single DataFrame with all matches
                completed_data = []
                for index, week in enumerate(included_weeks):
                    #print(len(all_matches_weekly_list), 'dfs')
                    #print(included_weeks)
                    completed_data.append(all_matches_weekly_list[index].iloc[selector.select_by_event_week([week], all_matches_weekly_list[index])])
                
                self.X = pd.concat(completed_data)
                self.X.pop('event_key')
                self.X.pop('key')
                #self.X.pop('Unnamed: 0')
                logger.debug(self.X.winning_alliance.sample(5))
                self.y = self.X.pop('winning_alliance')
                def add_one(x):
                    if x is None:
                        x = 0
                    return x+1
                self.y = self.y.apply(add_one)
                
                try:
                    self.model.fit(self.X,self.y)
                except Exception as e:
                    logger.exception('Something went wrong fitting data.')
                    logger.debug(self.X.columns)
                    raise e
            self.fit_weeks = included_weeks


        elif self.mode == 'default':
            try:
                self.model.fit(X, y)
            except Exception as e:
                logger.debug('Invalid values passed for X and y.', exc_info=True)
            

    def predict(self, X=False, included_weeks=[], verbose=True):
        """
        calls the model's predict method.
        X=False: pass arguments to directly call model's predict function
        """

        if type(X) == bool:  # :(
            if not X:
                if self.enable_sql:
                    all_events = pd.read_sql('events', engine)
                else:
                    all_events = pd.read_json(self.event_data_filepath)
                team_stats = setup.team_stats_process(included_weeks=self.fit_weeks, team_stats_filepath=False, directory='match_expanded_tba', late_weighting=self.late_weighting, sql_mode=self.enable_sql)
                logger.debug('Processed final team statistics.')

                def includedevents(x: int):
                    if x in included_weeks:
                        return True
                    elif -1 in included_weeks:
                        if x not in [0,1,2,3,4,5]:
                            return True
                    else:
                        return False
                
                X = setup.load_matches_alliance_stats(all_matches_stats_filepath=False, event_keys=list(all_events.loc[all_events['week'].apply(includedevents)]['key']), verbose=True, enable_sql=self.enable_sql, 
                    team_stats_filepath=team_stats, all_matches_filepath='match_dictionary')
                
                X.to_csv('sample_test_data.csv')
                logger.debug('Loaded per match statistics for test data.')
                logger.debug(X)
                self.y_test = X.pop('winning_alliance').map(lambda x: x+1) 
                X.pop('event_key')
                X.pop('key')

        self.predict_weeks=included_weeks
        return self.model.predict(X)
    
    def score(self, y_test=False, prediction_weeks=[]):
        """
        Method that takes in both the actual values and the bad values,
        y_test=False -- pass False to use the data that was not predicted. Pass another value to have those compared
        """
        logger.debug('Starting scoring...')
        predictions = self.predict(included_weeks=prediction_weeks)
        if not y_test:
            y_test = self.y_test
        score = accuracy_score(predictions, y_test)
        logger.info(f'Test ran with params: late weighting: {self.late_weighting}, \n model: {type(self.model)}, \n training weeks: {self.fit_weeks},\n prediction weeks: {prediction_weeks}, \n score: {score}')
        return score

    def optimize(self):
        """
        Method that uses optuna to create a study to optomize the model. Custom models cannot use this method.
        """
        if self.mode == 'XGBoost':
            pass
    

if __name__ == '__main__':
    model = FRCModel(mode='week_by_week')
    model.fit(included_weeks='all', data_preloaded_filepath='old code/data', write_data=True)