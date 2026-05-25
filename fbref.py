import requests
from bs4 import BeautifulSoup, Comment
import time
import pandas as pd
import os

class MatchData:
    def __init__(self) -> None:
        self.comp = ""
        self.data = ""
        self.round = ""
        self.data = {}
    
class PlayerData:
    def __init__(self) -> None:
        self.data = []
        self.base_url = ""
        self.matches_links = []
        self.matches = []
        self.match_stat_set = set()


def fetch_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    html = response.text
    parsed_html = BeautifulSoup(html, 'html.parser')
    comments = parsed_html.find_all(string=lambda text: isinstance(text, Comment))