import requests

BASE_URL = "https://fantasy.premierleague.com/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

def fetch_bootstrap():
    url = f"{BASE_URL}/bootstrap-static/"
    headers = {**HEADERS, "Referer": url}
    r = requests.get(url, headers = headers, timeout = 30)
    r.raise_for_status()
    return r.json()

def fetch_fixtures():
    url = f"{BASE_URL}/fixtures/"
    headers = {**HEADERS, "Referer": url}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_player_summary(player_id):
    url = f"{BASE_URL}/element-summary/{player_id}/"
    headers = {**HEADERS, "Referer": url}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_manager_history(entry_id):
    url = f"{BASE_URL}/entry/{entry_id}/history/"
    headers = {**HEADERS, "Referer": url}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()
def fetch_manager_transfers(entry_id):
    url = f"{BASE_URL}/entry/{entry_id}/transfers/"
    headers = {**HEADERS, "Referer": url}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_manager_gw_picks(entry_id, gw):
    url = f"{BASE_URL}/entry/{entry_id}/event/{gw}/picks/"
    headers = {**HEADERS, "Referer": url}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_manager_standings(league_id, page):
    url = f"{BASE_URL}/leagues-classic/{league_id}/standings/?page_standings={page}"
    headers = {**HEADERS, "Referer": url}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_manager_personal_data(entry_id):
    url = f"{BASE_URL}/entry/{entry_id}/"
    headers = {**HEADERS, "Referer": url}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()
