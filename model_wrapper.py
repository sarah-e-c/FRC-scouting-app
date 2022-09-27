from concurrent.futures import process
import pandas as pd
from xgboost import XGBClassifier, XGBRegressor
import match_selector as selector
import data_handling.process_data as setup
import optuna
import os
from sklearn.metrics import accuracy_score
import logging
from data_handling import models, session, engine
from sqlalchemy import String, Integer, Float

NON_WEEK_TABLE_NAME_CODE = 10
logger = logging.getLogger(__name__)
class FRCModel():
    """
    Class to be used like sklearn-like ML model. Has features specific to the data.
    """
    def __init__(self, model='XGBoost', mode='files', late_weighting=False):
        """
        model='XGBoost' -- either supported string or other model that supports fit() and transform()
        mode- 'files' -- supported modes
        teams_directory='teams_data' -- directory where the teams are held
        late_weighting=False -- value for experimental late weighting for teams 
        """

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

        logger.debug(f'FRCModel created. params:\n mode: {self.mode}\n, late weighting: {self.late_weighting}, \n model: {type(self.model)}')
        

    def fit(self, X=False, y=False, fit_weeks=[]):
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


        if fit_weeks == 'all':
            fit_weeks = [0,1,2,3,4,5,-1] # all weeks represented
            all_fit_weeks = True
        elif type(fit_weeks) == str:
            fit_weeks = eval(fit_weeks)
            all_fit_weeks = False
        else:
            all_fit_weeks = False
        self.fit_weeks = fit_weeks
        # incomplete default files mode
        if self.mode == 'files':
            pass

            # setup.team_stats_process(late_weighting=False)
        
        #week by week mode: evaluating team stats based on data evaluated weekly (recommended)
        #WARNING: this mode is currently very time intensive and needs to be optomized
        elif ((self.mode == 'week_by_week') and not all_fit_weeks):
            # calculating averages 

            setup.clear_temp_tables()
            processed_weeks = []
            for week in fit_weeks:
                processed_weeks.append(week)
                # just avoiding some negative weirdness
                if week != -1:
                    setup.team_stats_process_full_sql('match_expanded_tba', output_table_name=f'temp_teams_profile_week_{week}', filter=setup.get_basic_filter(included_events='all', included_weeks=processed_weeks), late_weighting=self.late_weighting)
                else: 
                    setup.team_stats_process_full_sql('match_expanded_tba', output_table_name=f'temp_teams_profile_week_{NON_WEEK_TABLE_NAME_CODE}', filter=setup.get_basic_filter(included_events='all', included_weeks=processed_weeks), late_weighting=self.late_weighting)

            
            for index, week in enumerate(fit_weeks):
                filter = setup.get_basic_filter(included_weeks=[week], included_events='all')
                if week != -1:
                    setup.load_matches_alliance_stats_full_sql('match_dictionary', f'temp_teams_profile_week_{week}', 'temp_matches', 'events', filter, delete_existing=False)
                else:   
                    setup.load_matches_alliance_stats_full_sql('match_dictionary', f'temp_teams_profile_week_{NON_WEEK_TABLE_NAME_CODE}', 'temp_matches', 'events', filter, delete_existing=False) # is pushing into the same database

            logger.debug('Finished generating match specific data sheets.')
            
            #returning a single DataFrame with all matches
            self.X = pd.read_sql('temp_matches', engine)

            
            #self.X = pd.concat(completed_data)
            self.X.pop('event_key')
            self.X.pop('key')
            
            self.X = self.X.loc[self.X['winning_alliance'].apply(lambda x: x in ['red', 'blue'])]
            self.y = self.X.pop('winning_alliance')
            self.y = self.y.map({'red': 1, 'blue': -1, '': 0, None:0, 'Red': 1, 'Blue': -1})
            self.y.iloc[0] = 0

        elif ((self.mode == 'week_by_week') and all_fit_weeks): # simplified version without temp tables -- speeds up considerably
            # calculating averages 

            setup.clear_temp_tables()
            
            #returning a single DataFrame with all matches
            matches_dfs = []
            for week in fit_weeks:
                if week != -1:
                    matches_dfs.append(pd.read_sql(f'all_matches_stats_week_{week}', engine))
                else:
                    matches_dfs.append(pd.read_sql('all_matches_stats_all_weeks', engine)) # the name is bad

            # concatenating all of the matches from the places
            self.X = pd.concat(matches_dfs)
            
            #self.X = pd.concat(completed_data)
            self.X.pop('event_key')
            self.X.pop('key')
            
            self.X = self.X.loc[self.X['winning_alliance'].apply(lambda x: x in ['red', 'blue'])]
            self.y = self.X.pop('winning_alliance')
            self.y = self.y.map({'red': 1, 'blue': -1, '': 0, None:0, 'Red': 1, 'Blue': -1})
            self.y.iloc[0] = 0


            self.y = self.y.map(lambda x: x+1)
            try:
                self.model.fit(self.X,self.y)
            except Exception as e:
                logger.exception('Something went wrong fitting data.')
                logger.warning(self.X)
                raise e
            self.latest_team_data=f'temp_teams_profile_week_{fit_weeks[len(fit_weeks) - 1]}'

        elif self.mode == 'default':
            try:
                self.model.fit(X, y)
            except Exception as e:
                logger.debug('Invalid values passed for X and y.', exc_info=True)
            

    def predict(self, X=False, predict_weeks=[]):
        """
        calls the model's predict method.
        X=False: pass arguments to directly call model's predict function
        """
        
        if len(predict_weeks) > 0: # predict weeks are specified
            filter_ = setup.get_basic_filter(included_weeks=predict_weeks, included_events='all')
            setup.load_matches_alliance_stats_full_sql('match_dictionary', self.latest_team_data, 'temp_matches', 'events', filter_, delete_existing=True)
        
            X = pd.read_sql('temp_matches', engine)
            # removing unnecessary languages
            self.y_test = X.pop('winning_alliance')
            self.y_test = self.y_test.map({'red': 1, 'blue': -1, '': 0, None:0, 'Red': 1, 'Blue': -1})
            self.y_test = self.y_test.map(lambda x: x+1)
            X.pop('event_key')
            X.pop('key')

            return self.model.predict(X)
        
        else:
            return self.model.predict(X)
    
    def score(self, prediction_weeks: list, y_test=False):
        """
        Method that takes in both the actual values and the bad values,
        y_test=False -- pass False to use the data that was not predicted. Pass another value to have those compared
        """
        logger.debug('Starting scoring...')
        predictions = self.predict(predict_weeks=prediction_weeks)
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
    import time
    start = time.time()
    model = FRCModel(mode='week_by_week', late_weighting=False)
    model.fit(fit_weeks=[0,1,2,3,4])
    print(model.score([5,-1]))
    print(time.time() - start)
    #model.predict(included_weeks='all')