
import os
import pandas as pd

def save_teams(data, output_dir):
    teams_dir = os.path.join(output_dir, 'teams')
    os.makedirs(teams_dir, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(teams_dir, 'teams.csv'), index=False)

def save_fixtures(data, output_dir):
    fixtures_dir = os.path.join(output_dir, 'fixtures')
    os.makedirs(fixtures_dir, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(fixtures_dir, 'fixtures.csv'), index=False)

def save_players_raw(data, output_dir):
    players_dir = os.path.join(output_dir, 'players')
    os.makedirs(players_dir, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(players_dir, 'players_raw.csv'), index=False)

def save_best_players(events, output_dir):
    rows =[]
    for event in events:
        if event['finished']:
            rows.append({
                'gw': event['id'],
                'player_id': event['top_element'],
                'points': event['top_element_info']['points']
            })
    players_dir = os.path.join(output_dir, 'players')
    os.makedirs(players_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(players_dir, 'best_players.csv'), index=False)

def save_player_history(data, player_name, player_id, output_dir):
    player_history_dir = os.path.join(output_dir, 'players',f"{player_name}_{player_id}")
    os.makedirs(player_history_dir, exist_ok=True)
    df = pd.DataFrame(data['history_past'])
    df.to_csv(os.path.join(player_history_dir, 'history.csv'), index=False)

def save_player_gw(data, player_name, player_id, output_dir):
    player_gw_dir = os.path.join(output_dir, 'players', f"{player_name}_{player_id}")
    os.makedirs(player_gw_dir, exist_ok=True)
    df = pd.DataFrame(data['history'])
    df.to_csv(os.path.join(player_gw_dir, 'gw.csv'), index=False)

def save_managers(data, output_dir):
    managers_dir = os.path.join(output_dir, 'managers')
    os.makedirs(managers_dir, exist_ok=True)
    df = pd.DataFrame(data)[['rank', 'entry', 'player_name', 'entry_name', 'total']]
    df.to_csv(os.path.join(managers_dir, 'top_managers.csv'), index=False)

def save_manager_history(data, entry_id, output_dir):
    manager_history_dir = os.path.join(output_dir, 'managers', f"{entry_id}")
    os.makedirs(manager_history_dir, exist_ok=True)
    df = pd.DataFrame(data['current'])
    df.to_csv(os.path.join(manager_history_dir, 'gws.csv'), index=False)

def save_manager_transfers(data, entry_id, output_dir):
    manager_transfers_dir = os.path.join(output_dir, 'managers', f"{entry_id}")
    os.makedirs(manager_transfers_dir, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(manager_transfers_dir, 'transfers.csv'), index=False)

def save_manager_gw_picks(data, entry_id, gw, output_dir):
    manager_gw_picks_dir = os.path.join(output_dir, 'managers',f"{entry_id}")
    os.makedirs(manager_gw_picks_dir, exist_ok=True)
    df = pd.DataFrame(data['picks'])[['element', 'position', 'multiplier']]
    df.to_csv(os.path.join(manager_gw_picks_dir, f"gw_{gw}.csv"), index=False)

def save_manager_chips(data, entry_id, output_dir):
    manager_chips_dir = os.path.join(output_dir, 'managers', f"{entry_id}")
    os.makedirs(manager_chips_dir, exist_ok=True)
    df = pd.DataFrame(data['chips'])
    df.to_csv(os.path.join(manager_chips_dir, 'chips.csv'), index=False)

def save_manager_past_seasons(data, entry_id, output_dir):
    manager_past_seasons_dir = os.path.join(output_dir, 'managers', f"{entry_id}")
    os.makedirs(manager_past_seasons_dir, exist_ok=True)
    df  = pd.DataFrame(data['past'])
    df.to_csv(os.path.join(manager_past_seasons_dir, 'past_seasons.csv'), index=False)

def save_manager_leagues(data, entry_id, output_dir):
    manager_dir = os.path.join(output_dir, 'managers', f"{entry_id}")
    os.makedirs(manager_dir, exist_ok=True)
    classic_leagues_df = pd.DataFrame(data['leagues']['classic'])
    h2h_leagues_df = pd.DataFrame(data['leagues']['h2h'])
    classic_leagues_df.to_csv(os.path.join(manager_dir, 'classic_leagues.csv'), index=False)
    h2h_leagues_df.to_csv(os.path.join(manager_dir, 'h2h_leagues.csv'), index=False)
    try:
        pd.DataFrame(data['leagues']['cup']['matches']).to_csv(
            os.path.join(manager_dir, 'cup_leagues.csv'), index=False)
    except KeyError:
        print(f"No cup data for manager {entry_id}")



