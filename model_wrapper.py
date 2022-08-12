import pandas as pd
from xgboost import XGBClassifier
import match_selector as selector
import data_setup as setup
import optuna
import os
from sklearn.metrics import accuracy_score

class FRCModel():
    def __init__(self, model='XGBoost', mode='files', teams_directory='teams_data', late_weighting=False, event_data_filepath='about_all_events.json'):
        """
        model='XGBoost' -- either supported string or other model that supports fit() and transform()
        mode- 'files' -- supported modes
        teams_directory='teams_data' -- directory where the teams are held
        late_weighting=False -- value for experimental late weighting for teams 
        """

        self.event_data_filepath = event_data_filepath
        self.mode = mode
        self.late_weighting = late_weighting
        # list of supported models
        if model =='XGBoost':
            self.model = XGBClassifier()
        else:
            self.model = model

        
        # modes
        if mode=='files':
            self.teams_directory = teams_directory
        

    def fit(self, X=False, y=False, included_weeks=[], data_preloaded_filepath=False, write_data=False):
        """
        \b
        |  method to fit the model. Calls the model's fit method. \n
        |  mode='default': 'default' - pass in X and y to directly fit the model, 'week_by_week' to use the files to load separate team stats for each week \n
        |  X=False: pass False if using file mode, but pass pandas DataFrame if using default method (an error will be thrown if not) \n
        |  y=False: pass False if using file mode, but pass pandas Series if using default method (an error will be thrown if not) \n
        |  included_weeks=[]: pass a list to select which weeks to include (use -1 last), or pass 'all' to get all of the weeks \n
        |  data_preloaded_filepath: pass a string of the first folders in order for the data to not be processed and instead read. \n
        |  write_data: pass True to write the processed data to csv files.
        """


        if included_weeks == 'all':
            included_weeks = [0,1,2,3,4,5,-1] # all weeks represented

        # incomplete default files mode
        if self.mode == 'files':
            pass
            # setup.team_stats_process(late_weighting=False)
        
        #week by week mode: evaluating team stats based on data evaluated weekly (recommended)
        #WARNING: this mode is currently very time intensive and needs to be optomized
        elif self.mode == 'week_by_week':
            all_events = pd.read_json(self.event_data_filepath)
            
            #user passed False
            if not data_preloaded_filepath:
                weeks_processed = []
                weeks_dfs = []
                for week in included_weeks:
                    weeks_processed.append(week)
                    weeks_dfs.append(setup.team_stats_process(team_stats_filepath=False, included_weeks=weeks_processed, late_weighting=self.late_weighting, verbose=False))
                
                #write data just processed to csv for faster testing/use
                if write_data:
                    for df, week in zip(weeks_dfs, included_weeks):
                        df.to_csv(f'old code/data/match_data_by_cum_week/week-{week}-data')
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
                        all_matches_weekly_list.append(setup.load_matches_alliance_stats(team_stats_filepath=weeks_dfs[index], event_keys=all_events.loc[all_events['week'] == week]['key'], verbose=True, all_matches_stats_filepath=False))
                    else: 
                        all_matches_weekly_list.append(setup.load_matches_alliance_stats(team_stats_filepath=weeks_dfs[index], event_keys=all_events.loc[all_events['week'].apply(lambda x: x not in [0,1,2,3,4,5])]['key'], verbose=True, all_matches_stats_filepath=False))
                if write_data:
                    for df, week in zip(all_matches_weekly_list, included_weeks):
                        df.to_csv(f'old code/data/match_data_by_cum_week/week_{week}_match_data')
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
            
            self.y = self.X.pop('winning_alliance')
            self.y = self.y.map(lambda x: x+1)
            

            self.model.fit(self.X,self.y)
            self.fit_weeks = included_weeks

            print(all_matches_weekly_list)

        elif self.mode == 'default':
            try:
                self.model.fit(X, y)
            except Exception as e:
                print(e)
                print('Please pass valid values for X and y.')
            

    def predict(self, X=False, included_weeks=[], team_stats_filepath='all_team_stats.csv'):
        """
        calls the model's predict method.
        X=False: pass arguments to directly call model's predict function
        """

        if not X:
            all_events = pd.read_json(self.event_data_filepath)
            team_stats = setup.team_stats_process(included_weeks=self.fit_weeks, team_stats_filepath=False, directory='teams_data')
            def includedevents(x: int):
                if x in included_weeks:
                    return True
                elif -1 in included_weeks:
                    if x not in [0,1,2,3,4,5]:
                        return True
                else:
                    return False
            X = setup.load_matches_alliance_stats(all_matches_stats_filepath=False, event_keys=all_events.loc[all_events['key'].apply(includedevents)]['key'], verbose=True, 
                team_stats_filepath=team_stats)
            print(X.columns)
            
            self.y_test = X.pop('winning_alliance').map(lambda x: x+1)
            X.pop('event_key')

        self.predict_weeks=included_weeks
        return self.model.predict(X)
    
    def score(self, y_test=False, prediction_weeks=[]):
        """
        Method that takes in both the actual values and the bad values,
        y_test=False -- pass False to use the data that was not predicted. Pass another value to have those compared
        """
        predictions = self.predict(included_weeks=prediction_weeks)
        if not y_test:
            y_test = self.y_test
        return accuracy_score(predictions, y_test)

    def optimize(self):
        """
        uses optuna to create a study to optomize the model. Custom models cannot use this method.
        """
        if self.mode == 'XGBoost':
            pass
    

if __name__ == '__main__':
    model = FRCModel(mode='week_by_week')
    model.fit(included_weeks='all', data_preloaded_filepath='old code/data', write_data=True)