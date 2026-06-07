from fpl_getters import (
    fetch_bootstrap,
    fetch_player_summary,
    fetch_manager_history,
    fetch_manager_transfers,
    fetch_manager_gw_picks,
    fetch_manager_standings,
    fetch_manager_personal_data,
)
from fpl_parsers import (
    save_players_raw,
    save_best_players,
    save_player_history,
    save_player_gw,
    save_managers,
    save_manager_history,
    save_manager_transfers,
    save_manager_gw_picks,
    save_manager_chips,
    save_manager_past_seasons,
    save_manager_leagues,
    save_cleaned_players,
    save_xp,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
import pandas as pd
import re
from pathlib import Path

OUTPUT_DIR = os.path.join("data", "FPL", "2025")
OVERALL_LEAGUE_ID = 314
TOP_MANAGERS = 1000
MAX_WORKERS = 10


def get_completed_gws(events):
    finished_event_ids = []
    for event in events:
        if event["finished"]:
            finished_event_ids.append(event["id"])
    return finished_event_ids


def fetch_and_save_player(player, output_dir):
    """Fetch and save one player's history and GW data."""
    player_id = player["id"]
    player_name = (player["first_name"] + "_" + player["second_name"]).replace(" ", "_")
    try:
        data = fetch_player_summary(player_id)
        save_player_history(data, player_name, player_id, output_dir)
        save_player_gw(data, player_name, player_id, output_dir)
        return player_name, None
    except Exception as e:
        return player_name, str(e)


def run_player_pipeline(players, events, output_dir):
    save_players_raw(players, output_dir)
    save_best_players(events, output_dir)
    failed = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_and_save_player, player, output_dir): player
            for player in players
        }

        with tqdm(total=len(players), desc="fetching players") as pbar:
            for future in as_completed(futures):
                player_name, error = future.result()
                if error:
                    failed.append((str(player_name), str(error)))
                pbar.update(1)

    if failed:
        pd.DataFrame(failed, columns=["player_name", "error"]).to_csv(
            os.path.join(output_dir, "failed_players.csv"), index=False
        )


def fetch_manager_history_transfers_gw_picks(entry_id, completed_gws, output_dir):
    try:
        history = fetch_manager_history(entry_id)
        save_manager_history(history, entry_id, output_dir)
        save_manager_chips(history, entry_id, output_dir)
        save_manager_past_seasons(history, entry_id, output_dir)

        personal_data = fetch_manager_personal_data(entry_id)
        save_manager_leagues(personal_data, entry_id, output_dir)

        save_manager_transfers(fetch_manager_transfers(entry_id), entry_id, output_dir)
        for gw in completed_gws:
            data = fetch_manager_gw_picks(entry_id, gw)
            save_manager_gw_picks(data, entry_id, gw, output_dir)
        return str(entry_id), None
    except Exception:
        import traceback

        return str(entry_id), traceback.format_exc()


def run_manager_pipeline(output_dir, completed_gws):
    all_managers = []
    for page in range(1, 21):
        data = fetch_manager_standings(OVERALL_LEAGUE_ID, page)
        all_managers.extend(data["standings"]["results"])
    save_managers(all_managers, output_dir)
    failed = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(
                fetch_manager_history_transfers_gw_picks,
                manager["entry"],
                completed_gws,
                output_dir,
            ): manager
            for manager in all_managers
        }

        with tqdm(total=len(all_managers), desc="Fetching managers") as pbar:
            for future in as_completed(futures):
                entry_id, error = future.result()
                if error:
                    failed.append((str(entry_id), str(error)))
                pbar.update(1)

    if failed:
        pd.DataFrame(failed, columns=["entry_id", "error"]).to_csv(
            os.path.join(output_dir, "managers", "failed_managers.csv"), index=False
        )


def merge_player_names(output_dir):
    players_df = pd.read_csv(os.path.join(output_dir, "players", "players_raw.csv"))
    players_df["player_name"] = (
        players_df["first_name"] + " " + players_df["second_name"]
    )
    players_df = players_df[["id", "player_name"]]
    root_dir = Path(os.path.join(output_dir, "managers"))
    pattern = re.compile(r"gw_\d+\.csv$")
    for gw_file in root_dir.rglob("*.csv"):
        if pattern.search(gw_file.name):
            gw_df = pd.read_csv(gw_file)[["element", "position", "multiplier"]]
            merged_df = gw_df.merge(
                players_df, left_on="element", right_on="id", how="left"
            )
            merged_df = merged_df[["element", "position", "multiplier", "player_name"]]
            merged_df.to_csv(gw_file, index=False)


def build_gw_files(output_dir):
    players_df = pd.read_csv(os.path.join(output_dir, "players", "players_raw.csv"))
    players_df["name"] = players_df["first_name"] + " " + players_df["second_name"]
    teams_df = pd.read_csv(os.path.join(output_dir, "teams", "teams.csv"))
    teams_df = teams_df[["id", "name"]].rename(columns={"name": "team_name"})
    players_df = players_df.merge(teams_df, left_on="team", right_on="id", how="left")
    position_mapped = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
    players_df["position"] = players_df["element_type"].map(position_mapped)
    players_df = players_df[["id_x", "position", "name", "team_name"]].rename(
        columns={"id_x": "id", "team_name": "team"}
    )
    # print(players_df.columns.tolist())
    # print(players_df.head())
    root_dir = Path(os.path.join(output_dir, "players"))
    pattern = re.compile(r"gw\.csv$")
    all_gws = []
    for gw_file in root_dir.rglob("*.csv"):
        if pattern.search(gw_file.name):
            gw_df = pd.read_csv(gw_file)
            gw_df = gw_df.merge(
                players_df, left_on="element", right_on="id", how="left"
            )
            all_gws.append(gw_df)
    combined_df = pd.concat(all_gws, ignore_index=True)
    gws_folder = os.path.join(output_dir, "gws")
    os.makedirs(gws_folder, exist_ok=True)
    for round_num, group in combined_df.groupby("round"):
        group.to_csv(os.path.join(gws_folder, f"gw_{round_num}.csv"), index=False)


def get_current_gw(events):
    for event in events:
        if event["is_current"]:
            return event["id"]
    return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    bootstrap = fetch_bootstrap()

    # players = bootstrap['elements']
    # events = bootstrap['events']
    # teams = bootstrap['teams']
    # completed_gws = get_completed_gws(events)

    # save_teams(teams, OUTPUT_DIR)
    # save_fixtures(fetch_fixtures(), OUTPUT_DIR)
    # run_player_pipeline(players, events, OUTPUT_DIR)
    # run_manager_pipeline(OUTPUT_DIR, completed_gws)
    # merge_player_names(OUTPUT_DIR)
    build_gw_files(OUTPUT_DIR)
    # save_xp(bootstrap, OUTPUT_DIR)
    save_cleaned_players(OUTPUT_DIR)  # add this
    save_xp(bootstrap, OUTPUT_DIR)


if __name__ == "__main__":
    main()
