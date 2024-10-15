import requests
import json
import pandas as pd
from datetime import datetime
import os


class BettingAPI:
    
    def __init__(self, path_to_args, league) -> None:

        self.name = 'BettingAPI'
        with open(path_to_args, 'r', encoding='utf-8') as json_file:
            private_kargs = json.load(json_file)
        self.api_params = private_kargs['betting_api_params']

        self.SPORT = self.api_params["SPORT"][league] # https://the-odds-api.com/sports-odds-data/sports-apis.html
        # self.event_name = os.path.splitext(os.path.basename(private_kargs['path_to_html']))[0]
        self.league = league
        self.API_KEY = self.api_params['API_KEY']
        self.REGIONS = self.api_params['REGIONS']
        self.odds = pd.DataFrame()
        self.update_odds()


    def json_to_df(self, json_response) -> pd.DataFrame:
        avg_odds = {}

        for bookmaker in json_response[0]['bookmakers']:
            for team in bookmaker['markets'][0]['outcomes']:
                if team['name'] not in avg_odds.keys():
                    avg_odds[team['name']] = {}
                avg_odds[team['name']][bookmaker['title']] = team['price']

        odds_df = pd.DataFrame.from_dict(avg_odds, orient='index')
        odds_df['mean_odd'] = odds_df.mean(axis='columns').apply(round, ndigits=2)
        odds_df['max_odd'] = odds_df.max(axis='columns')
        
        return odds_df
 

    def update_odds(self) -> None:
        url = f'https://api.the-odds-api.com//v4/sports/{self.SPORT}/odds/?apiKey={self.API_KEY}&regions={self.REGIONS}'
        try:
            odds_response = requests.get(
                url=url)
            if odds_response.status_code != 200:
                print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
            else:
                odds_json = odds_response.json() 
                self.odds = self.json_to_df(odds_json)
                self.odds.to_csv(f'database_files/{self.league}_odds_{datetime.now().date()}_{datetime.now().hour}.csv', index_label=False) # maybe move to polymarket_lib

                print('Remaining requests', odds_response.headers['x-requests-remaining'])
                print('Used requests', odds_response.headers['x-requests-used'])
                self.last_update_time = datetime.now()
        except Exception as e:
            print(e)
        
        return None
