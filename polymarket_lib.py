import os
import pandas as pd
from polymarket_connector import Polymarket_connector, Market
from database import Database
from betting_api_connector import BettingAPI
from datetime import datetime, timedelta

# api_key = os.getenv("api_key")
# To make sure it stays secret, create a file called .env containing api_key=YOUR_API_KEY


class Polymarket_MM:

    def __init__(self, path_to_args, league):
        self.name = 'Polymarket_MM'
        self.path_to_args = path_to_args
        self.league = league

        self.polymarket_connector = Polymarket_connector(path_to_args)
        self.database = Database(path_to_args, league)
        self.condition_ids = self.database.read_condition_ids()
        self.bet_api = BettingAPI(path_to_args, league)

        self.markets = []
        for id in self.condition_ids:
            self.markets.append(Market(self.polymarket_connector.client, id, league))
        self.last_update_markets = datetime.now()
        print('Polymarket_MM ready to make money!')

    
    def run_signal(self, margin: float, min_prob: float) -> pd.DataFrame:

        # update data
        if (datetime.now() - self.bet_api.last_update_time).seconds > 60*30:
            self.bet_api.update_odds()
        if (datetime.now() - self.last_update_markets).seconds > 60*30:
            self.update_markets()

        yes_ba = pd.DataFrame(
            [{'polymarket_team_name': market.team_name, 'price': float(market.yes_best_ask.price)} for market in self.markets]
            )
        yes_ba.set_index('polymarket_team_name', inplace=True)

        no_ba = pd.DataFrame(
            [{'polymarket_team_name': market.team_name, 'price': float(market.no_best_ask.price)} for market in self.markets]
            )
        no_ba.set_index('polymarket_team_name', inplace=True)
        
        df = self.database.map_table.assign(
            yes_ba_price=yes_ba['price'],
            no_ba_price=no_ba['price']
            )

        df.set_index('bet_api_name', inplace=True)
        res = self.bet_api.odds[['mean_odd','max_odd']].assign(
            yes_ba_price=df['yes_ba_price'],
            no_ba_price=df['no_ba_price']
        )
        res['implied_prob'] = 1/(res['max_odd']*margin)
        res['yes_overprice'] = res['implied_prob']/res['yes_ba_price'] - 1
        res['no_overprice'] = (1-res['implied_prob'])/res['no_ba_price'] - 1

        res = res.map(round, ndigits=4)
        res = res[res['implied_prob'] >= min_prob]
        res = res.sort_values(by='yes_overprice', ascending=False)

        return res
    

    def update_markets(self) -> None:

        for market in self.markets:
            market.update_market()

        self.last_update_markets = datetime.now()

        return None



    

