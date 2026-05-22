import pandas as pd

players_df = pd.read_csv('data/FPL/2025/players/players_raw.csv')
players_df['player_name'] = players_df['first_name'] + ' ' + players_df['second_name']
players_df = players_df[['id', 'player_name']]

gw_df = pd.read_csv('data/FPL/2025/managers/44/gw_1.csv')[['element', 'position', 'multiplier']]

merged = gw_df.merge(players_df, left_on='element', right_on='id', how='left')
print(merged.columns.tolist())
print(merged.head())