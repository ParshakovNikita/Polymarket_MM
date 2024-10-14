from py_clob_client.constants import POLYGON, AMOY
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
import json


class Polymarket_connector:


    def __init__(self, path_to_args) -> None:

        self.name = 'Polymarket_connector'

        with open(path_to_args, 'r', encoding='utf-8') as json_file:
            private_kargs = json.load(json_file)

        self.host = private_kargs['host']
        self.key = private_kargs['key']
        self.chain_id = POLYGON

        self.client = ClobClient(host=self.host, key=self.key, chain_id=self.chain_id)
        self.client.set_api_creds(self.client.create_or_derive_api_creds())
        print('Succesfully auth with Poly')


class Market:

    def __init__(self, client: ClobClient, condition_id: str) -> None:
        self.name = 'Market'
        self.client = client
        self.condition_id = condition_id
        self.update_market()

        try:
            self.team_name = self.extract_team_name(self.question)
        except Exception as e:
            self.team_name = ""
            print(e)

    def update_market(self) -> None:
        market_dict = self.client.get_market(condition_id=self.condition_id)

        self.question = market_dict['question']
        self.description = market_dict['description']
        self.minimum_order_size = market_dict['minimum_order_size']

        for token in market_dict['tokens']:
            if token['outcome'] == 'Yes':
                self.yes_token_id = token['token_id']
                self.yes_token_price = token['price']
                self.yes_token_order_book = self.client.get_order_book(token_id=self.yes_token_id)
                self.yes_best_bid = self.yes_token_order_book.bids[-1]
                self.yes_best_ask = self.yes_token_order_book.asks[-1]
            elif token['outcome'] == 'No':
                self.no_token_id = token['token_id']
                self.no_token_price = token['price']
                self.no_token_order_book = self.client.get_order_book(token_id=self.no_token_id)
                self.no_best_bid = self.no_token_order_book.bids[-1]
                self.no_best_ask = self.no_token_order_book.asks[-1]
        del market_dict

        return None
    

    def extract_team_name(self, question) -> str:
        words = question.split()
        if len(words) >= 3 and words[0] == "Will" and words[-4] == "win":
            return words[2]
        return None

