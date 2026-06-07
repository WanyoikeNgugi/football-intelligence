import requests
import os
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

LEAGUES = ["EPL", "La_liga", "Bundesliga", "Serie_A", "Ligue_1"]
SEASONS = list(range(2014, 2026))
MAX_WORKERS = 10
CURRENT_SEASON = 2025

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

#  Fetchers


def fetch_league_data(league, season):
    url = f"https://understat.com/getLeagueData/{league}/{season}"
    headers = {**HEADERS, "Referer": f"https://understat.com/league/{league}/{season}"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_player_data(player_id):
    url = f"https://understat.com/getPlayerData/{player_id}"
    headers = {**HEADERS, "Referer": f"https://understat.com/player/{player_id}"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_fpl_players():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    r = requests.get(url, timeout=50)
    r.raise_for_status()
    return r.json()["elements"]


# Savers


def save_team_data(teams, output_dir):
    for _, team in teams.items():
        team_name = team["title"].replace(" ", "_")
        team_dir = os.path.join(output_dir, "teams", team_name)
        os.makedirs(team_dir, exist_ok=True)
        pd.DataFrame(team["history"]).to_csv(
            os.path.join(team_dir, f"{team_name}.csv"), index=False
        )


def save_players_data(players, output_dir):
    players_dir = os.path.join(output_dir, "players")
    os.makedirs(players_dir, exist_ok=True)
    pd.DataFrame(players).to_csv(os.path.join(players_dir, "players.csv"), index=False)


def save_single_player(player, players_dir):
    player_id = player["id"]
    player_name = player["player_name"].replace(" ", "_")
    try:
        data = fetch_player_data(player_id)

        pd.DataFrame(data["matches"]).to_csv(
            os.path.join(players_dir, f"{player_name}_{player_id}.csv"), index=False
        )

        pd.DataFrame(data["shots"]).to_csv(
            os.path.join(players_dir, f"{player_name}_{player_id}_shots.csv"),
            index=False,
        )
        return player_name, None

    except Exception as e:
        return player_name, str(e)


def save_player_match_data(players_list, output_dir):
    players_dir = os.path.join(output_dir, "players")
    os.makedirs(players_dir, exist_ok=True)
    failed = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(save_single_player, player, players_dir): player
            for player in players_list
        }

        with tqdm(total=len(players_list), desc="Fetching players") as pbar:
            for future in as_completed(futures):
                player_name, error = future.result()
                if error:
                    failed.append((player_name, error))
                pbar.update(1)

    if failed:
        print(f"\n{len(failed)} players failed:")
        for name, err in failed:
            print(f"  {name}: {err}")
        failed_df = pd.DataFrame(failed, columns=["player_name", "error"])
        failed_df.to_csv(os.path.join(output_dir, "failed_players.csv"), index=False)


def save_fpl_players(outout_dir):
    elements = fetch_fpl_players()
    df = pd.DataFrame(elements)[["id", "first_name", "second_name"]]
    df.to_csv(os.path.join(outout_dir, "player_idlist.csv"), index=False)


def match_ids(output_dir):
    understat_df = pd.read_csv(os.path.join(output_dir, "players", "players.csv"))
    fpl_df = pd.read_csv(os.path.join(output_dir, "player_idlist.csv"))
    fpl_df["player_name"] = fpl_df["first_name"] + " " + fpl_df["second_name"]

    fpl_lookup = fpl_df.set_index("player_name")["id"].to_dict()
    us_lookup = understat_df.set_index("player_name")["id"].to_dict()
    all_names = set(fpl_lookup) | set(us_lookup)

    rows = []
    for name in all_names:
        rows.append(
            {
                "Understat_ID": us_lookup.get(name, -1),
                "FPL_ID": fpl_lookup.get(name, -1),
                "Understat_Name": name if name in us_lookup else "",
                "FPL_Name": name if name in fpl_lookup else "",
            }
        )

    pd.DataFrame(rows).to_csv(os.path.join(output_dir, "id_dict.csv"), index=False)


# Pipeline


def run_pipeline(league, season):
    output_dir = os.path.join("data", league, str(season))
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"Processing {league} {season}/{season+1}")
    print(f"{'='*50}")

    try:
        data = fetch_league_data(league, season)
        save_team_data(data["teams"], output_dir)
        save_players_data(data["players"], output_dir)
        save_player_match_data(data["players"], output_dir)

        if league == "EPL" and season == CURRENT_SEASON:
            save_fpl_players(output_dir)
            match_ids(output_dir)
            print("✓ FPL ID matching complete")

        print(f"✓ {league} {season} complete")
    except Exception as e:
        print(f"✗ {league} {season} failed: {e}")


if __name__ == "__main__":
    for league in LEAGUES:
        for season in tqdm(SEASONS, desc=f"{league}"):
            run_pipeline(league, season)
            time.sleep(1)
