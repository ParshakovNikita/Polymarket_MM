import os
import json
import re
from typing import List
import pandas as pd


class Database():

    def __init__(self, path_to_args, league):

        self.name = "Database"
        with open(path_to_args, 'r', encoding='utf-8') as json_file:
            private_kargs = json.load(json_file)

        self.path_to_html = private_kargs['path_to_html'][league]
        self.path_to_data = private_kargs['path_to_data']
        self.path_to_map_file = private_kargs['path_to_map_file']
        self.map_table = pd.read_excel(self.path_to_map_file, index_col='polymarket_team_name')

    def html_parser(self) -> List:

        with open(self.path_to_html, 'r', encoding='utf-8') as file:
            html_content = file.read()
            pattern = r'"conditionId"\s*:\s*"([^"]+)"'
            condition_ids = list(set(re.findall(pattern, html_content)))

        return condition_ids
    
    def read_txt_ids(self) -> List:

        with open(self.path_to_data, 'r') as file:
            condition_ids = [line.strip() for line in file.readlines()]

        return condition_ids
    
    def read_condition_ids(self) -> List[str]:

        try:
            condition_ids = self.read_txt_ids()
            if not condition_ids:
                return self.html_parser()
        except FileNotFoundError:
            return self.html_parser()
        
        return condition_ids