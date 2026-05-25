import pandas as pd
import os

print(pd.read_csv('data/FPL/2025/players/cleaned_players.csv').head())
print(os.listdir('data/FPL/2025/gws'))
print(pd.read_csv('data/FPL/2025/gws/gw_1.csv').columns.tolist())